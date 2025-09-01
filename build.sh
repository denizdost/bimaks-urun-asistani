# Render.com için build script
#!/bin/bash
# build.sh

echo "🚀 Bimaks Ürün Asistanı - Build Script"
echo "======================================"

# Python paketlerini yükle
pip install -r requirements.txt

# Uygulamayı başlat
echo "✅ Uygulama başlatılıyor..."
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
