import os
import openai
from typing import List, Dict, Any
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class LLMProcessor:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable bulunamadı!")
        
        openai.api_key = self.api_key
        self.model = "gpt-4o-mini"
    
    def analyze_recommendations(self, prompt: str, products: List[Dict[str, Any]]) -> Dict[str, str]:
        """Ürün önerilerini analiz et ve yapılandırılmış yanıt oluştur"""
        
        # Ürün bilgilerini formatla
        products_text = ""
        for i, product in enumerate(products, 1):
            products_text += f"""
Ürün {i}: {product['product_name']}
Kategori: {product['category']}
Uygulamalar: {', '.join(product['applications'])}
Çözülen Problemler: {', '.join(product['problems_solved'])}
Önemli Parametreler: {', '.join(product['key_params'])}
Kısa Açıklama: {product['short_desc']}
"""
        
        system_prompt = """Sen bir kimya şirketi için ürün öneren uzman asistanısın. 
Müşterinin ihtiyacına göre önerilen ürünleri analiz et ve yapılandırılmış bir yanıt ver.

Yanıtını şu JSON formatında ver:
{
    "summary": "Müşterinin ihtiyacının kısa özeti ve önerilen çözüm",
    "safety": "Güvenlik uyarıları ve dikkat edilmesi gerekenler",
    "follow_up": "Sonraki adımlar ve öneriler"
}

Önemli noktalar:
- Teknik terimleri açıkla
- Güvenlik konularına özel dikkat göster
- Pratik öneriler ver
- Türkçe yanıt ver
"""

        user_prompt = f"""
Müşteri İhtiyacı: {prompt}

Önerilen Ürünler:
{products_text}

Lütfen bu ürünleri analiz et ve yukarıdaki formatta yanıt ver.
"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # JSON yanıtını parse et
            content = response.choices[0].message.content.strip()
            
            # Basit JSON parsing (gerçek uygulamada daha güvenli parsing kullan)
            try:
                import json
                result = json.loads(content)
                return {
                    "summary": result.get("summary", "Analiz tamamlandı."),
                    "safety": result.get("safety", "Güvenlik bilgisi mevcut değil."),
                    "follow_up": result.get("follow_up", "Detaylı bilgi için iletişime geçin.")
                }
            except json.JSONDecodeError:
                # JSON parse edilemezse manuel parsing
                return self._parse_manual_response(content)
                
        except Exception as e:
            print(f"OpenAI API hatası: {e}")
            return {
                "summary": "Ürün analizi tamamlandı.",
                "safety": "Güvenlik bilgileri için teknik ekibimizle iletişime geçin.",
                "follow_up": "Detaylı bilgi ve fiyat teklifi için bize ulaşın."
            }
    
    def _parse_manual_response(self, content: str) -> Dict[str, str]:
        """JSON parse edilemezse manuel parsing"""
        lines = content.split('\n')
        summary = ""
        safety = ""
        follow_up = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if '"summary"' in line or 'summary' in line.lower():
                current_section = 'summary'
                summary = line.split(':', 1)[-1].strip().strip('"')
            elif '"safety"' in line or 'safety' in line.lower():
                current_section = 'safety'
                safety = line.split(':', 1)[-1].strip().strip('"')
            elif '"follow_up"' in line or 'follow_up' in line.lower():
                current_section = 'follow_up'
                follow_up = line.split(':', 1)[-1].strip().strip('"')
            elif current_section:
                if current_section == 'summary':
                    summary += " " + line.strip('"')
                elif current_section == 'safety':
                    safety += " " + line.strip('"')
                elif current_section == 'follow_up':
                    follow_up += " " + line.strip('"')
        
        return {
            "summary": summary or "Ürün analizi tamamlandı.",
            "safety": safety or "Güvenlik bilgileri için teknik ekibimizle iletişime geçin.",
            "follow_up": follow_up or "Detaylı bilgi ve fiyat teklifi için bize ulaşın."
        }
