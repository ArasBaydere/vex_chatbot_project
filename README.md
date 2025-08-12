# VEX V5 Robotics Competition Chatbot

🤖 **Akıllı VEX Robotik Chatbotu** - VEX V5 Robotics Competition kuralları ve yönetmelikleri için AI destekli asistan

## 🌟 Özellikler

- **🎯 Tam VEX V5RC Kural Desteği**: 103 temiz VEX V5RC kuralı, tam açıklamalarıyla
- **🇹🇷🇺🇸 İki Dilli Destek**: Türkçe ve İngilizce sorulara akıllı yanıtlar
- **🧠 RAG (Retrieval-Augmented Generation)**: FAISS vektör veritabanı ile hızlı ve doğru kural arama
- **⚡ Gerçek Zamanlı Sorgulama**: Google Gemini AI ile anlık yanıtlar
- **🎨 Kullanıcı Dostu Arayüz**: Gradio ile modern web arayüzü

## 🔧 Teknoloji Stack

- **Python 3.11+**
- **Google Generative AI** (Gemini-1.5-flash)
- **FAISS** - Vektör veritabanı
- **Gradio** - Web arayüzü
- **PyPDF2** - PDF işleme
- **Sentence Transformers** - Metin embedding

## 📁 Proje Yapısı

```
vex_chatbot_project/
├── src/
│   ├── chatbot_app.py      # Ana chatbot uygulaması
│   ├── data_processing.py   # PDF veri işleme
│   ├── embedding.py         # FAISS vektör veritabanı
│   └── rag_engine.py       # RAG motor ve sorgulama
├── data/
│   ├── game_manual.pdf     # VEX oyun kılavuzu
│   ├── processed_chunks.json  # İşlenmiş kurallar
│   ├── v5rc_complete_rules.json  # Tam kurallar
│   └── faiss_index.bin     # FAISS indeksi
├── requirements.txt        # Python bağımlılıkları
└── README.md              # Bu dosya
```

## 🚀 Kurulum

### 1. Repository'yi klonlayın
```bash
git clone https://github.com/ArasBaydere/vex_chatbot_project.git
cd vex_chatbot_project
```

### 2. Sanal ortam oluşturun
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 3. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### 4. Google AI API anahtarını ayarlayın
```bash
# Windows
set GOOGLE_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_API_KEY=your_api_key_here
```

### 5. FAISS indeksini oluşturun (gerekirse)
```bash
python src/embedding.py
```

## 🎯 Kullanım

### Chatbot'u Başlatın
```bash
python src/chatbot_app.py
```

Tarayıcınızda `http://localhost:7860` adresine gidin.

### Örnek Sorular

**Türkçe:**
- "R25 plastik kuralı nedir?"
- "Robot ağırlık limiti kaç?"
- "Plastik kullanım kuralları neler?"

**İngilizce:**
- "What is the R25 plastic rule?"
- "What are the robot weight limits?"
- "How many motors can I use?"

## 📊 Veri İşleme

### Kuralları Yeniden İşlemek
```bash
python src/data_processing.py
```

### Vektör Veritabanını Güncellemek
```bash
python src/embedding.py
```

## 🔍 Öne Çıkan Kurallar

- **R25**: Plastik kullanım kuralları (12 adet, 4"x8"x0.070" max)
- **R12**: Motor limitleri (88W toplam güç)
- **SG3**: Dikey genişleme (22" max yükseklik)
- **GG17**: Tutma kuralları (5 saniye max)

## 🛠️ Geliştirme

### Yeni Özellik Ekleme
1. `src/` klasöründe ilgili modülü düzenleyin
2. Testleri çalıştırın
3. Pull request oluşturun

### Kural Veritabanını Güncelleme
1. `data/game_manual.pdf` dosyasını güncelleyin
2. `python src/data_processing.py` çalıştırın
3. `python src/embedding.py` ile vektör veritabanını yenileyin

## 📜 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'i push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📞 İletişim

- **GitHub**: [@ArasBaydere](https://github.com/ArasBaydere)
- **Proje Linki**: [https://github.com/ArasBaydere/vex_chatbot_project](https://github.com/ArasBaydere/vex_chatbot_project)

## 🙏 Teşekkürler

- VEX Robotics Inc. - Oyun kılavuzu ve kurallar için
- Google - Gemini AI API için
- Facebook Research - FAISS kütüphanesi için

---

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**