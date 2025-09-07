import json
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ProductSearch:
    def __init__(self, data_path: str = "data/products.jsonl"):
        self.data_path = data_path
        self.products = self._load_products()
        self.vectorizer = None
        self.product_vectors = None
        self._build_search_index()
    
    def _load_products(self) -> List[Dict[str, Any]]:
        """JSONL dosyasından ürünleri yükle"""
        products = []
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        products.append(json.loads(line))
            print(f"✅ {len(products)} ürün yüklendi")
            return products
        except FileNotFoundError:
            print(f"❌ Dosya bulunamadı: {self.data_path}")
            return []
        except Exception as e:
            print(f"❌ Veri yükleme hatası: {e}")
            return []
    
    def _name_from_url(self, url: str) -> str:
        try:
            slug = (url or '').rstrip('/').rsplit('/', 1)[-1]
            name = slug.replace('-', ' ').strip()
            # Kısa MAKS kodlarını büyük yaz
            return name.upper()
        except Exception:
            return ''
    
    def _is_generic_name(self, name: str) -> bool:
        n = (name or '').strip().lower()
        if len(n) <= 8:
            return True
        generic_keys = (
            'hakkımızda', 'sertifikalar', 'insan kaynakları', 'gizlilik', 'politikası',
            'ürün grupları', 'ürün grubu', 'soğutma suyu ıslahı', 'su ve proses',
            'haberler', 'etkinlik', 'teknik', 'e-bülten'
        )
        return any(k in n for k in generic_keys)
    
    def _is_valid_product(self, p: Dict[str, Any]) -> bool:
        """Kategori/menü sayfalarını ve hatalı URL'leri ele"""
        url = (p.get('url') or '').lower()
        name = (p.get('product_name') or '').lower()
        if not url.startswith('http'):
            return False
        if 'info@' in url:
            return False
        banned = ('urun-gruplar', 'urun-gruplari', 'hammaddeler', 'haberler', 'etkinlik', 'teknik-', 'iletisim', 'bulten', 'nasil-dogru')
        if any(b in url for b in banned):
            return False
        depth = [seg for seg in url.split('/') if seg and 'http' not in seg]
        # Bazı gerçek ürün linkleri 3 segment olabiliyor; son slug içinde 'maks' veya rakam/kimyasal ipucu varsa kabul et
        if len(depth) >= 4:
            return True
        if len(depth) >= 3:
            leaf = depth[-1]
            if any(k in leaf for k in ('maks', 'antiskal', 'temizleyici', 'korozyon', 'biyosit', 'urunu', 'kimyasal')):
                return True
        return False
    
    def _normalize_products(self):
        normalized: List[Dict[str, Any]] = []
        for p in self.products:
            # URL/isim filtresi
            if not self._is_valid_product(p):
                continue
            name = p.get('product_name') or ''
            if self._is_generic_name(name):
                fallback = self._name_from_url(p.get('url', ''))
                if fallback:
                    p['product_name'] = fallback
            # short_desc boş ise kısalt
            short_desc = (p.get('short_desc') or '').strip()
            if not short_desc or len(short_desc) < 5:
                p['short_desc'] = p['product_name']
            normalized.append(p)
        self.products = normalized
    
    def _build_search_index(self):
        """TF-IDF vektörleri oluştur"""
        if not self.products:
            return
        
        # Normalize & filtrele
        self._normalize_products()
        
        # Her ürün için arama metni oluştur
        search_texts = []
        for product in self.products:
            text_parts = [
                product.get('product_name', ''),
                product.get('category', ''),
                ' '.join(product.get('applications', [])),
                ' '.join(product.get('problems_solved', [])),
                ' '.join(product.get('key_params', [])),
                product.get('short_desc', '')
            ]
            search_texts.append(' '.join(text_parts).lower())
        
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,
            ngram_range=(1, 2)
        )
        self.product_vectors = self.vectorizer.fit_transform(search_texts)
        print("✅ Arama indeksi oluşturuldu")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.products or self.vectorizer is None:
            return []
        query_vector = self.vectorizer.transform([query.lower()])
        similarities = cosine_similarity(query_vector, self.product_vectors).flatten()
        top_indices = np.argsort(similarities)[::-1][:max(top_k*5, top_k)]
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                product = self.products[idx].copy()
                if self._is_valid_product(product):
                    product['similarity_score'] = float(similarities[idx])
                    results.append(product)
            if len(results) >= top_k:
                break
        # Eğer çok sıkı filtreden dolayı sonuç çıkmadıysa, en yakın skorları yumuşak filtreyle döndür
        if not results:
            soft = []
            for idx in np.argsort(similarities)[::-1]:
                if similarities[idx] <= 0:
                    break
                p = self.products[idx].copy()
                p['similarity_score'] = float(similarities[idx])
                soft.append(p)
                if len(soft) >= top_k:
                    break
            return soft
        return results
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        return self.products
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [p for p in self.products if p.get('category', '').lower() == category.lower()]
