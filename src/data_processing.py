import fitz  # PyMuPDF'un diğer adı
import re
import json

def parse_game_manual(pdf_path):
    """
    VEX Game Manual'u okur, metinleri çıkarır ve kural ID'lerine göre parçalara ayırır.
    
    Args:
        pdf_path (str): Oyun kılavuzunun PDF dosya yolu.
        
    Returns:
        list: Her bir elemanı {'page_number': int, 'rule_id': str, 'content': str}
              formatında olan bir sözlük listesi.
    """
    
    document = fitz.open(pdf_path)
    parsed_chunks = []
    
    # Tüm kural ID'lerini yakalamak için daha genel bir regex deseni.
    # Örnek: <SC1>, <GG1>, <VUR1>, <VAISC1> gibi kalıpları bulur.
    rule_pattern = re.compile(r'<\s*([A-Z]{1,5}\d+)\s*>')
    
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text = page.get_text("text")
        
        # Kural ID'lerini ayraç olarak kullanıyoruz.
        chunks = rule_pattern.split(text)
        
        # İlk parça genellikle sayfa başlığı veya kural öncesi metindir.
        # Eğer bir kural ID'si bulunmuşsa, döngüyü başlatıyoruz.
        if len(chunks) > 1:
            for i in range(1, len(chunks), 2):
                rule_id = chunks[i]
                content = chunks[i+1].strip()
                
                # İçeriğin boş olup olmadığını kontrol et.
                if content:
                    chunk = {
                        'page_number': page_num + 1,  # Sayfa numaraları 1'den başlar
                        'rule_id': f'<{rule_id}>',
                        'content': content
                    }
                    parsed_chunks.append(chunk)
                    
    return parsed_chunks

if __name__ == "__main__":
    # Proje kök dizininden çalıştırıldığını varsayalım.
    pdf_path = "data/game_manual.pdf"
    
    try:
        chunks = parse_game_manual(pdf_path)
        print(f"Toplam {len(chunks)} parça ayrıştırıldı.")
        if chunks:
            print("İlk 3 parça:")
            for chunk in chunks[:3]:
                print(f"Sayfa: {chunk['page_number']}, Kural: {chunk['rule_id']}")
                print("-" * 20)
                
        # İsteğe bağlı: Ayrıştırılmış parçaları bir JSON dosyasına kaydetmek
        # with open("data/processed_chunks.json", "w", encoding="utf-8") as f:
        #     json.dump(chunks, f, ensure_ascii=False, indent=4)
        # print("\nAyrıştırılmış parçalar 'data/processed_chunks.json' dosyasına kaydedildi.")

    except FileNotFoundError:
        print(f"Hata: '{pdf_path}' dosyası bulunamadı. Lütfen dosyanın 'data' dizini altında olduğundan emin olun.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")