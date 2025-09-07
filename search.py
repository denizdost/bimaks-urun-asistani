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
    
    def _is_valid_product(self, p: Dict[str, Any]) -> bool:
        """Kategori/menü sayfalarını ve hatalı URL'leri ele"""
        url = (p.get('url') or '').lower()
        name = (p.get('product_name') or '').lower()
        if not url.startswith('http'):  # statik/pdf vs.
            return False
        if 'info@' in url:
            return False
        # genel menü/kategori kelimeleri
        banned = ('urun-gruplar', 'urun gruplar', 'hammaddeler', 'haberler', 'etkinlik', 'teknik-', 'iletisim', 'bulten', 'nasil-dogru')
        if any(b in url for b in banned):
            return False
        # isim çok genel ise (örn: "ürün grupları")
        if 'grubu' in name or 'ürünleri' == name or name.strip() in ('ürün grupları', 'ters osmoz ürünleri'):
            return False
        # derinlik kontrolü: /a/b/c/d en az 4 segment
        depth = [seg for seg in url.split('/') if seg and 'http' not in seg]
        return len(depth) >= 4
    
    def _build_search_index(self):
        """TF-IDF vektörleri oluştur"""
        if not self.products:
            return
        
        # Sadece geçerli ürünleri indeksle
        self.products = [p for p in self.products if self._is_valid_product(p)]
        
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
        
        # TF-IDF vektörleri oluştur
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # Türkçe stop words eklenebilir
            ngram_range=(1, 2)
        )
        self.product_vectors = self.vectorizer.fit_transform(search_texts)
        print("✅ Arama indeksi oluşturuldu")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Prompt'a göre en uygun ürünleri bul"""
        if not self.products or self.vectorizer is None:
            return []
        
        # Query'yi vektöre çevir
        query_vector = self.vectorizer.transform([query.lower()])
        
        # Cosine similarity hesapla
        similarities = cosine_similarity(query_vector, self.product_vectors).flatten()
        
        # En yüksek skorlu ürünleri al
        top_indices = np.argsort(similarities)[::-1][:max(top_k*2, top_k)]  # biraz daha fazla al, sonra filtrele
        
        # Sonuçları döndür (geçerli URL şartı)
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                product = self.products[idx].copy()
                if self._is_valid_product(product):
                    product['similarity_score'] = float(similarities[idx])
                    results.append(product)
            if len(results) >= top_k:
                break
        
        return results
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Tüm ürünleri döndür"""
        return self.products
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Kategoriye göre ürünleri filtrele"""
        return [p for p in self.products if p.get('category', '').lower() == category.lower()]
