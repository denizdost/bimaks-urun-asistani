# Render.com Deployment Guide
# Bimaks Ürün Asistanı - Canlı Website Kurulumu

## 🚀 Render.com ile Ücretsiz Deployment

### 1. GitHub'a Yükle
```bash
# Git repository oluştur
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/bimaks-urun-asistani.git
git push -u origin main
```

### 2. Render.com'da Yeni Servis Oluştur
1. https://render.com'a git
2. "New +" → "Web Service"
3. GitHub repository'ni bağla
4. Ayarlar:
   - **Name:** bimaks-urun-asistani
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

### 3. Environment Variables Ekle
Render dashboard'da:
- `OPENAI_API_KEY`: your_openai_api_key_here

### 4. Deploy Et
"Create Web Service" butonuna tıkla

## 🌐 Diğer Deployment Seçenekleri

### Railway.app
- GitHub bağla
- Auto-deploy aktif
- Environment variables ekle

### Heroku
- Heroku CLI kur
- `heroku create bimaks-urun-asistani`
- `git push heroku main`

### DigitalOcean App Platform
- GitHub bağla
- Python environment seç
- Environment variables ekle

## 🔧 Production Optimizasyonları

### 1. CORS Ayarları
```python
# main.py'de güncelle
allow_origins=["https://yourdomain.com"]
```

### 2. Environment Variables
```bash
# .env dosyası
OPENAI_API_KEY=your_real_api_key
DEBUG=False
```

### 3. Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 📊 Monitoring

### Health Check
```bash
curl https://your-app.onrender.com/health
```

### API Test
```bash
curl -X POST "https://your-app.onrender.com/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

## 🎯 Sonuç
- ✅ Ücretsiz hosting
- ✅ Otomatik deployment
- ✅ SSL sertifikası
- ✅ Custom domain desteği
- ✅ API ve web interface
