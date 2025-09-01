from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from search import ProductSearch
from llm import LLMProcessor

app = FastAPI(title="Bimaks Ürün Asistanı", version="1.0.0")

# CORS ayarları (frontend için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain belirt
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static dosyaları serve et
app.mount("/static", StaticFiles(directory="templates"), name="static")

# Global instances
product_search = ProductSearch()
llm_processor = LLMProcessor()

class RecommendationRequest(BaseModel):
    prompt: str

class Product(BaseModel):
    product_name: str
    category: str
    applications: List[str]
    problems_solved: List[str]
    key_params: List[str]
    short_desc: str
    url: str

class RecommendationResponse(BaseModel):
    summary: str
    products: List[Product]
    safety: str
    follow_up: str

@app.get("/")
async def root():
    return FileResponse("templates/index.html")

@app.get("/web")
async def web_interface():
    return FileResponse("templates/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api")
async def api_info():
    return {"message": "Bimaks Ürün Asistanı API'si çalışıyor!"}

@app.post("/api/recommend", response_model=RecommendationResponse)
async def recommend_products(request: RecommendationRequest):
    try:
        # 1. Prompt'a göre ürün ara
        relevant_products = product_search.search(request.prompt, top_k=3)
        
        if not relevant_products:
            raise HTTPException(status_code=404, detail="Uygun ürün bulunamadı")
        
        # 2. LLM ile analiz yap
        analysis = llm_processor.analyze_recommendations(request.prompt, relevant_products)
        
        return RecommendationResponse(
            summary=analysis["summary"],
            products=relevant_products,
            safety=analysis["safety"],
            follow_up=analysis["follow_up"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Öneri oluşturulurken hata: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
