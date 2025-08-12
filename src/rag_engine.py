import google.generativeai as genai
import faiss
import numpy as np
import os
import json
import re
from functools import lru_cache

# Türkçe-İngilizce keyword mapping
TURKISH_ENGLISH_KEYWORDS = {
    # Robot ve boyut terimleri
    'robot': 'robot',
    'boyut': 'size',
    'boyutlar': 'dimensions',
    'boyutları': 'dimensions', 
    'ölçü': 'size',
    'ölçüler': 'dimensions',
    'ölçüleri': 'dimensions',
    'sınır': 'limit',
    'sınırı': 'limit',
    'sınırlar': 'limits',
    'sınırları': 'limits',
    'ağırlık': 'weight',
    'maksimum': 'maximum',
    'minimum': 'minimum',
    'genişleme': 'expansion',
    'hacim': 'volume',
    'kübik': 'cubic',
    'inç': 'inch',
    'santimetre': 'centimeter',
    'milimetre': 'millimeter',
    
    # Malzeme terimleri
    'plastik': 'plastic',
    'polikarbonat': 'polycarbonate',
    'polikarbonate': 'polycarbonate',
    'özel': 'custom',
    'malzeme': 'material',
    'metal': 'metal',
    'parça': 'part',
    'parçalar': 'parts',
    'bileşen': 'component',
    'miktarda': 'amount',
    'miktar': 'amount',
    'sınırlı': 'limited',
    'izin': 'allowed',
    'yasak': 'illegal',
    
    # Oyun terimleri
    'oyun': 'game',
    'maç': 'match',
    'müsabaka': 'competition',
    'turnuva': 'tournament',
    'puan': 'point',
    'skor': 'score',
    'gol': 'goal',
    'hedef': 'target',
    
    # Kural terimleri
    'kural': 'rule',
    'kurallar': 'rules',
    'yasak': 'illegal',
    'izin': 'legal',
    'ceza': 'penalty',
    'ihlal': 'violation',
    
    # Teknik terimler
    'motor': 'motor',
    'güç': 'power',
    'batarya': 'battery',
    'sensör': 'sensor',
    'program': 'program',
    'otonom': 'autonomous',
    'manuel': 'manual',
    'kontrol': 'control',
    'kumanda': 'control'
}

def translate_query_keywords(query):
    """
    Türkçe sorguyu İngilizce anahtar kelimelerle zenginleştir
    """
    query_lower = query.lower()
    translated_terms = []
    
    for turkish, english in TURKISH_ENGLISH_KEYWORDS.items():
        if turkish in query_lower:
            translated_terms.append(english)
    
    # Orijinal sorgu + İngilizce terimler
    enhanced_query = query + " " + " ".join(translated_terms)
    return enhanced_query

# Proje ana dizininden çalıştırıldığını varsayalım
script_dir = os.path.dirname(os.path.abspath(__file__))
chunks_path = os.path.join(script_dir, "..", "data", "processed_chunks.json")
faiss_index_path = os.path.join(script_dir, "..", "data", "faiss_index.bin")

# API Anahtarını çevre değişkeninden al
API_KEY = os.getenv("GOOGLE_API_KEY", "your_api_key_here")
genai.configure(api_key=API_KEY)

# FAISS indeksini ve metin parçalarını bir kere yükle ve önbelleğe al
@lru_cache(maxsize=1)
def load_data():
    try:
        index = faiss.read_index(faiss_index_path)
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        print("FAISS indeksi ve metin parçaları başarıyla yüklendi.")
        return index, chunks
    except Exception as e:
        print(f"Hata: Veritabanı dosyaları yüklenemedi. Hata: {e}")
        return None, None

def get_related_chunks(query, k=30):
    """
    Kullanıcı sorgusuyla en alakalı metin parçalarını ve meta verilerini geri getirir.
    Daha geniş bir arama havuzundan kelime tabanlı filtreleme yapar.
    
    Args:
        query (str): Kullanıcı sorgusu.
        k (int): Geri getirilecek en alakalı parça sayısı.
        
    Returns:
        list: En alakalı metin parçalarının {'content', 'page_number', 'rule_id'} formatında listesi.
    """
    index, chunks = load_data()
    if not index or not chunks:
        print("HATA: Index veya chunks yüklenemedi!")
        return []

    print(f"\n=== DETAYLI DEBUG BAŞLANGICI ===")
    print(f"Orijinal sorgu: '{query}'")
    
    # Türkçe sorguyu İngilizce terimlerle zenginleştir
    enhanced_query = translate_query_keywords(query)
    print(f"Zenginleştirilmiş sorgu: '{enhanced_query}'")
    print(f"Toplam chunk sayısı: {len(chunks)}")
    
    # Enhanced query ile sorguyu vektörleştirme
    try:
        query_embedding = genai.embed_content(
            model='models/text-embedding-004', 
            content=enhanced_query,
            task_type="retrieval_query"
        )['embedding']
        query_embedding_np = np.array([query_embedding], dtype='float32')
        print(f"Query embedding başarıyla oluşturuldu, boyut: {len(query_embedding)}")
    except Exception as e:
        print(f"HATA: Query embedding oluşturulamadı: {e}")
        # API başarısız olursa, enhanced query ile anahtar kelime araması yap
        return keyword_only_search(enhanced_query, chunks)

    # FAISS'te en yakın komşuları arama
    try:
        distances, indices = index.search(query_embedding_np, k)
        print(f"FAISS arama tamamlandı, {len(indices[0])} sonuç bulundu")
        print(f"İlk 5 distance: {distances[0][:5]}")
        print(f"İlk 5 index: {indices[0][:5]}")
    except Exception as e:
        print(f"HATA: FAISS arama başarısız: {e}")
        return keyword_only_search(enhanced_query, chunks)
    
    retrieved_chunks = []
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks):
            chunk = {'content': chunks[idx]['content'], 'page_number': chunks[idx]['page_number'], 'rule_id': chunks[idx]['rule_id']}
            retrieved_chunks.append(chunk)
            if i < 5:  # İlk 5 chunk'ı debug için göster
                print(f"Chunk {i}: Sayfa {chunk['page_number']}, Kural {chunk['rule_id']}")
                print(f"İçerik özeti: {chunk['content'][:200]}...")
                print("---")

    # Anahtar kelimelerle ikincil filtreleme - daha kapsamlı kelime setleri
    # Hem orijinal sorgu hem de enhanced query'yi anahtar kelime belirlemede kullan
    combined_query = (query + " " + enhanced_query).lower()
    keywords = []
    
    # Boyut/ölçü soruları için
    if any(w in combined_query for w in ['boyut', 'size', 'ölçü', 'limit', 'sınır', 'dimension', 'ölçüler', 'büyüklük', 'dimensions']):
        keywords.extend(['boyut', 'size', 'ölçü', 'limit', 'sınır', 'dimension', 'dimensions', 'expansion', 'genişleme', 
                        '18', '22', 'inch', 'inç', 'mm', 'volume', 'hacim', 'cubic', 'kübik'])
        print("🔍 Boyut sorgusu algılandı")
        
    # Ağırlık soruları için  
    elif any(w in combined_query for w in ['ağırlık', 'weight', 'gram', 'kg', 'kilogram', 'kaç', 'ne kadar']):
        keywords.extend(['ağırlık', 'weight', 'gram', 'kg', 'kilogram', 'mass', 'kütle', 'block', 'blok', 
                        '40', 'approximately', 'yaklaşık'])
        print("⚖️ Ağırlık sorgusu algılandı")
        
    # Malzeme/plastik soruları için
    elif any(w in combined_query for w in ['plastik', 'plastic', 'polikarbonat', 'polycarbonate', 'malzeme', 'material', 'özel', 'custom', 'parça', 'part']):
        keywords.extend(['plastic', 'plastik', 'polycarbonate', 'polikarbonat', 'material', 'malzeme', 'custom', 'özel', 
                        'part', 'parça', 'component', 'bileşen', 'allowed', 'izin', 'limited', 'sınırlı', 'amount', 'miktar', 'R25'])
        print("🧪 Malzeme sorgusu algılandı")
        
    # Kural numarası soruları için (R1, R25, SG1 vb.)
    elif any(re.search(r'\b[RSG]+\d+\b', combined_query) for w in [combined_query]):
        # Kural numarasını çıkar
        rule_matches = re.findall(r'\b[RSG]+\d+\b', combined_query.upper())
        keywords.extend(rule_matches)
        keywords.extend(['rule', 'kural', 'regulation'])
        print(f"📋 Kural numarası sorgusu algılandı: {rule_matches}")
        
    # Robot soruları için
    elif 'robot' in combined_query:
        keywords.extend(['robot', 'robotics', 'competition', 'yarışma'])
        print("🤖 Robot sorgusu algılandı")
    
    # Hem orijinal hem enhanced query'deki kelimeleri anahtar kelimelere ekle
    combined_words = re.findall(r'\b\w{2,}\b', combined_query)  # 2+ karakter kelimeler
    keywords.extend(combined_words)
    
    # Temel anahtar kelimeler her zaman dahil
    keywords.extend(["rule", "kural", "regulation", "kural"])
    
    # Duplicate'ları kaldır
    keywords = list(set(keywords))
    print(f"Anahtar kelimeler: {keywords}")

    filtered_chunks = []
    for chunk in retrieved_chunks:
        content_lower = chunk['content'].lower()
        rule_id_lower = chunk['rule_id'].lower()
        
        # Her anahtar kelime için ayrı ayrı kontrol et
        matched_keywords = []
        for keyword in keywords:
            # Daha esnek eşleştirme
            if (keyword in content_lower or keyword in rule_id_lower or
                re.search(r'\b' + re.escape(keyword) + r'\b', content_lower) or
                re.search(r'\b' + re.escape(keyword) + r'\b', rule_id_lower)):
                matched_keywords.append(keyword)
        
        if matched_keywords:
            chunk['matched_keywords'] = matched_keywords
            filtered_chunks.append(chunk)
            print(f"✓ EŞLEŞME: Sayfa {chunk['page_number']}, Kural {chunk['rule_id']}, Kelimeler: {matched_keywords}")

    print(f"Filtreleme sonrası chunk sayısı: {len(filtered_chunks)}")

    # Eğer filtreleme sonucunda parça bulunamazsa, en üstteki 5 taneyi kullan
    if not filtered_chunks:
        print("⚠️ Hiç eşleşme bulunamadı, ilk 5 chunk kullanılacak")
        final_chunks_to_use = retrieved_chunks[:5]
    else:
        final_chunks_to_use = filtered_chunks[:5]
    
    print(f"\n--- FINAL CHUNKS ({len(final_chunks_to_use)} adet) ---")
    for i, chunk in enumerate(final_chunks_to_use):
        print(f"{i+1}. Sayfa: {chunk['page_number']}, Kural: {chunk['rule_id']}")
        if 'matched_keywords' in chunk:
            print(f"   Eşleşen kelimeler: {chunk['matched_keywords']}")
        print(f"   İçerik: {chunk['content'][:150]}...")
        print("")
    print("=== DETAYLI DEBUG SONU ===\n")

    return final_chunks_to_use

def keyword_only_search(query, chunks):
    """API başarısız olduğunda sadece anahtar kelime araması yapar."""
    print("🔄 API başarısız, anahtar kelime aramasına geçiliyor...")
    
    query_lower = query.lower()
    keywords = []
    
    # Boyut soruları
    if any(w in query_lower for w in ['boyut', 'size', 'ölçü', 'limit', 'sınır']):
        keywords.extend(['18', '22', 'inch', 'expansion', 'size', 'dimension', 'boyut', 'genişleme'])
        
    # Ağırlık soruları
    elif any(w in query_lower for w in ['ağırlık', 'weight', 'gram']):
        keywords.extend(['40', 'gram', 'weight', 'block', 'ağırlık'])
        
    # Sorgu kelimelerini ekle
    keywords.extend(re.findall(r'\b\w{2,}\b', query_lower))
    
    matching_chunks = []
    for chunk in chunks:
        content_lower = chunk['content'].lower()
        score = 0
        
        for keyword in keywords:
            if keyword in content_lower:
                score += 1
                
        if score > 0:
            chunk_copy = chunk.copy()
            chunk_copy['score'] = score
            matching_chunks.append(chunk_copy)
    
    # Score'a göre sırala
    matching_chunks.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Anahtar kelime araması: {len(matching_chunks)} chunk bulundu")
    return matching_chunks[:5]

def create_rag_prompt(query, related_chunks_with_metadata, history=None):
    """
    Gemini modeline gönderilecek nihai prompt'u oluşturur.
    
    Args:
        query (str): Kullanıcı sorgusu.
        related_chunks_with_metadata (list): En alakalı metin parçalarının ve meta verilerinin listesi.
        history (list): Sohbet geçmişi (opsiyonel).
        
    Returns:
        str: Gemini'ye gönderilecek prompt.
    """
    
    system_prompt = (
        "Sen, VEX Robotics 2025-2026 oyunu 'Push Back' konusunda uzman, yardımsever bir yapay zeka asistanısın. "
        "Amacın, VEX takımlarına oyun kılavuzuyla ilgili sordukları sorulara hızlı ve doğru cevaplar vermektir.\n\n"
        "Çok önemli: Cevaplarını SADECE sana sunulan 'KAYNAK METİNLER' bölümündeki bilgilere dayanarak, direkt ve doğru bir şekilde oluştur.\n"
        "Her cevabının sonuna, cevabı aldığın kuralı ve sayfa numarasını **(Kaynak: Sayfa X, Kural Y)** formatında mutlaka ekle.\n"
        "Eğer sorunun cevabı sana verilen kaynak metinlerde yoksa, şu formatta cevap ver:\n"
        "'Bu bilgi 2025-2026 Push Back oyun kılavuzunda mevcut değil. Ancak şu benzer bilgiler var: [benzer kural varsa belirt]'\n\n"
        "Özel durumlar:\n"
        "- Robot ağırlık sınırı sorulursa: '2025-2026 Push Back oyununda robot ağırlık sınırı belirtilmemiş. Sadece boyut sınırları var.'\n"
        "- Robot boyut/ölçü sorulursa: SG1, SG2, SG3 kurallarından cevap ver.\n"
        "- Plastik/malzeme sorulursa: R25 kuralından tam detayları ver. 'A limited amount of custom plastic is allowed' gibi kısa cevaplar verme, mümkünse ek kuralları da belirt.\n"
        "- Polikarbonat sorulursa: Polycarbonate panels field perimeter decorations için kullanılabilir.\n\n"
        "Cevaplarında VEX jargonunu kullanmaktan çekinme ve her zaman yardım odaklı, arkadaş canlısı bir dil kullan."
    )
    
    # RAG ile bulunan ilgili kuralları prompt'a ekliyoruz, meta verileriyle birlikte.
    context = "\n\nKAYNAK METİNLER:\n"
    for chunk in related_chunks_with_metadata:
        context += f"--- Sayfa {chunk['page_number']}, Kural {chunk['rule_id']}:\n{chunk['content']}\n\n"
    
    # Sohbet geçmişini ekliyoruz
    history_str = ""
    if history:
        for turn in history:
            history_str += f"\nKullanıcı: {turn['user']}\nAsistan: {turn['model']}\n"
    
    final_prompt = f"{system_prompt}{history_str}{context}\n\nKullanıcı: {query}\nAsistan:"
    
    return final_prompt

def get_answer_from_gemini(query):
    """
    Kullanıcı sorgusuna RAG mimarisiyle cevap üretir.
    
    Args:
        query (str): Kullanıcı sorgusu.
        
    Returns:
        str: Gemini modelinden gelen cevap.
    """
    if not load_data()[0] or not load_data()[1]:
        return "Üzgünüm, RAG veritabanı yüklenemedi. Lütfen sistem yöneticinizle iletişime geçin."

    try:
        related_chunks_with_metadata = get_related_chunks(query)
        
        if not related_chunks_with_metadata:
            return "Üzgünüm, sorgunuzla ilgili bilgi bulunamadı. Lütfen farklı kelimelerle tekrar deneyin."
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        final_prompt = create_rag_prompt(query, related_chunks_with_metadata)
        
        print(f"\n🤖 Gemini'ye gönderilen prompt uzunluğu: {len(final_prompt)} karakter")
        
        # Timeout ve retry ile API çağrısı
        import time
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Gemini API çağrısı (deneme {attempt + 1}/{max_retries})...")
                
                response = model.generate_content(
                    final_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Daha tutarlı cevaplar için
                        max_output_tokens=1000,
                    )
                )
                
                if response and response.text:
                    print("✅ Gemini API başarılı!")
                    return response.text
                else:
                    print("⚠️ Gemini boş cevap döndü")
                    
            except Exception as e:
                print(f"❌ Gemini API hatası (deneme {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 2, 4, 6 saniye bekle
                    print(f"⏳ {wait_time} saniye bekleniyor...")
                    time.sleep(wait_time)
                else:
                    # Son deneme başarısız olursa, fallback cevabı ver
                    return create_fallback_response(query, related_chunks_with_metadata)
                    
    except Exception as e:
        print(f"❌ Genel hata: {e}")
        return f"Üzgünüm, cevap oluşturulurken bir hata oluştu: {e}"

def create_fallback_response(query, chunks):
    """API başarısız olduğunda basit cevap oluşturur."""
    
    query_lower = query.lower()
    
    # Boyut soruları için
    if any(w in query_lower for w in ['boyut', 'size', 'ölçü', 'limit', 'sınır']):
        for chunk in chunks:
            if any(w in chunk['content'].lower() for w in ['18', '22', 'expansion']):
                return f"""2025-2026 Push Back oyununda robot boyut sınırları:

• Başlangıç: 18" x 18" x 18" (maksimum)
• Genişleme: 22" x 22" x 22" (maksimum)

**Kaynak: Sayfa {chunk['page_number']}, Kural {chunk['rule_id']}**"""

    # Ağırlık soruları için
    elif any(w in query_lower for w in ['ağırlık', 'weight', 'gram']):
        for chunk in chunks:
            if '40' in chunk['content'] and 'gram' in chunk['content'].lower():
                return f"""2025-2026 Push Back oyununda:

• **Robot ağırlık sınırı:** Belirtilmemiş
• **Block ağırlığı:** Yaklaşık 40 gram

**Kaynak: Sayfa {chunk['page_number']}, Kural {chunk['rule_id']}**"""
    
    # Genel fallback
    return "API bağlantı sorunu nedeniyle tam cevap oluşturulamadı. Lütfen tekrar deneyin."

def answer_question(query):
    """
    Soru cevaplama için ana fonksiyon wrapper'ı
    """
    return get_answer_from_gemini(query)

if __name__ == "__main__":
    # Test amaçlı
    test_query = "Robot ağırlık sınırı nedir?"
    answer = get_answer_from_gemini(test_query)
    print(f"Soru: {test_query}")
    print(f"Cevap: {answer}")