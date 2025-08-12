import google.generativeai as genai
import faiss
import numpy as np
import os
import json

# Proje ana dizininden çalıştırıldığını varsayalım.
script_dir = os.path.dirname(os.path.abspath(__file__))
chunks_path = os.path.join(script_dir, "..", "data", "processed_chunks.json")
faiss_index_path = os.path.join(script_dir, "..", "data", "faiss_index.bin")

# API Anahtarını çevre değişkeninden al
API_KEY = os.getenv("GOOGLE_API_KEY", "your_api_key_here")
genai.configure(api_key=API_KEY)

def create_embeddings_and_index(chunks):
    """
    Metin parçalarını vektörlere dönüştürür ve bir FAISS indeksine kaydeder.
    
    Args:
        chunks (list): parse_game_manual fonksiyonundan gelen metin parçaları listesi.
        
    Returns:
        faiss.IndexFlatL2: Oluşturulan FAISS indeksi.
    """
    
    model = 'models/text-embedding-004'
    embeddings = []
    
    print("Metin parçaları vektörlere dönüştürülüyor...")
    for chunk in chunks:
        try:
            response = genai.embed_content(model=model, content=chunk['content'])
            embeddings.append(response['embedding'])
        except Exception as e:
            print(f"Embedding oluşturulurken hata oluştu: {e}")
            continue
            
    embeddings_np = np.array(embeddings, dtype='float32')
    
    # FAISS indeksi oluşturma
    # D = Vektör boyutu (text-embedding-004 için 768)
    # L2 mesafesi (öklid mesafesi) kullanıyoruz.
    d = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings_np)
    
    return index

def create_faiss_index():
    """
    Mevcut processed_chunks.json'dan FAISS index oluşturur
    """
    try:
        # JSON dosyasından chunks'ları yükle
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        print(f"📊 {len(chunks)} chunk yüklendi")
        
        # Vektörleştirme ve FAISS indeksi oluşturma
        faiss_index = create_embeddings_and_index(chunks)
        
        # FAISS indeksini kaydetme
        faiss.write_index(faiss_index, faiss_index_path)
        
        print("✅ FAISS indeksi başarıyla oluşturuldu!")
        print(f"📁 Lokasyon: {faiss_index_path}")
        
        return faiss_index
        
    except FileNotFoundError:
        print(f"❌ Hata: '{chunks_path}' dosyası bulunamadı.")
        return None
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None

if __name__ == "__main__":
    create_faiss_index()