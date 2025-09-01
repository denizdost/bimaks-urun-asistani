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
    
    def _build_search_index(self):
        """TF-IDF vektörleri oluştur"""
        if not self.products:
            return
        
        # Her ürün için arama metni oluştur
        search_texts = []
        for product in self.products:
            text_parts = [
                product['product_name'],
                product['category'],
                ' '.join(product['applications']),
                ' '.join(product['problems_solved']),
                ' '.join(product['key_params']),
                product['short_desc']
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
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Sonuçları döndür
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Sadece pozitif benzerlik skorları
                product = self.products[idx].copy()
                product['similarity_score'] = float(similarities[idx])
                results.append(product)
        
        return results
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Tüm ürünleri döndür"""
        return self.products
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Kategoriye göre ürünleri filtrele"""
        return [p for p in self.products if p['category'].lower() == category.lower()]
