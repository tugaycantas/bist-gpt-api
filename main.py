from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="BIST Analiz GPT API")

# Model sınıfı
class StockQuery(BaseModel):
    symbol: str

# Dummy veri (sonra gerçek veriyi buraya entegre edebilirsin)
stock_prices = {
    "THYAO": 275.4,
    "ASELS": 46.7,
    "KRDMD": 14.2
}

kap_news = {
    "THYAO": "THYAO 2025 3. çeyrek bilançosunu yayımladı: Net kâr 12.3 milyar TL.",
    "ASELS": "ASELS yeni füze sistemleri ihracatı için anlaşma imzaladı.",
    "KRDMD": "KRDMD üretim kapasitesini %20 artırmayı planlıyor."
}

# Fonksiyonlar
@app.post("/get_stock_price")
async def get_stock_price(request: Request):
    data = await request.json()
    symbol = data.get("symbol", "").upper()

    price = stock_prices.get(symbol)
    if price is None:
        return {"symbol": symbol, "error": "Bilinmeyen hisse kodu"}

    return {"symbol": symbol, "price": price}
@app.post("/get_kap_news")
def get_kap_news(query: StockQuery):
    news = kap_news.get(query.symbol.upper(), None)
    if news is None:
        return {"symbol": query.symbol, "error": "KAP haberi bulunamadı"}
    return {"symbol": query.symbol.upper(), "news": news}

# Test endpoint
@app.get("/")
def root():
    return {"message": "BIST Analiz GPT API çalışıyor!"}
