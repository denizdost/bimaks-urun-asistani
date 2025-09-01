# 🧪 Bimaks Ürün Asistanı

Kimya şirketi için akıllı ürün öneren chatbot projesi.

## 🚀 Özellikler

- **Semantic Search**: TF-IDF ile akıllı ürün arama
- **AI Analiz**: OpenAI GPT-4o-mini ile ürün analizi
- **FastAPI Backend**: Modern ve hızlı API
- **JSON Response**: Yapılandırılmış yanıt formatı

## 📁 Proje Yapısı

```
bimaks_urun_asistani/
├── main.py              # FastAPI ana uygulama
├── search.py            # Ürün arama modülü
├── llm.py              # OpenAI API işlemleri
├── test_api.py         # API test scripti
├── requirements_fastapi.txt  # Python gereksinimleri
├── env_example.txt     # Environment variables örneği
├── data/
│   └── products.jsonl  # 10 ürünlük demo veri
└── README.md           # Bu dosya
```

## 🛠️ Kurulum

### 1. Gereksinimleri Yükle
```bash
pip install -r requirements_fastapi.txt
```

### 2. Environment Variables
```bash
# env_example.txt dosyasını .env olarak kopyala
cp env_example.txt .env

# OpenAI API key'ini ekle
echo "OPENAI_API_KEY=your_actual_api_key_here" >> .env
```

### 3. Uygulamayı Başlat
```bash
python main.py
```

API `http://localhost:8000` adresinde çalışacak.

## 🧪 Test

```bash
# API'yi test et
python test_api.py
```

## 📡 API Endpoints

### GET /
- **Açıklama**: Ana sayfa
- **Response**: `{"message": "Bimaks Ürün Asistanı API'si çalışıyor!"}`

### GET /health
- **Açıklama**: Sağlık kontrolü
- **Response**: `{"status": "healthy"}`

### POST /api/recommend
- **Açıklama**: Ürün önerisi
- **Request Body**:
```json
{
    "prompt": "Ters osmoz sistemimde kireçlenme problemi yaşıyorum"
}
```
- **Response**:
```json
{
    "summary": "Müşterinin ihtiyacının özeti...",
    "products": [
        {
            "product_name": "MAKS 400P TERS OSMOZ ANTİSKALANT (NSF)",
            "category": "Ters Osmoz",
            "applications": ["Ters osmoz sistemleri", "membran arıtma"],
            "problems_solved": ["Membran kireçlenmesi", "sistem tıkanması"],
            "key_params": ["NSF sertifikalı", "düşük dozaj"],
            "short_desc": "RO sistemleri için NSF sertifikalı antiskalant",
            "url": "https://www.bimakskimya.com.tr/..."
        }
    ],
    "safety": "Güvenlik uyarıları...",
    "follow_up": "Sonraki adımlar..."
}
```

## 🔧 Geliştirme

### Yeni Ürün Ekleme
1. `data/products.jsonl` dosyasına yeni ürün ekle
2. JSON formatında her satır bir ürün olmalı

### API Geliştirme
- `main.py`: Yeni endpoint'ler ekle
- `search.py`: Arama algoritmasını geliştir
- `llm.py`: LLM prompt'larını optimize et

## 🚀 Sonraki Adımlar

- [ ] Next.js frontend ekle
- [ ] Daha büyük ürün veritabanı
- [ ] Kullanıcı authentication
- [ ] Öneri geçmişi
- [ ] Fiyat bilgisi entegrasyonu

## 📞 Destek

Soruların için: [GitHub Issues](https://github.com/your-repo/issues)
