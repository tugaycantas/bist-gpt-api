from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict
import json
import io
import pandas as pd
import requests
from pypdf import PdfReader
import time

app = FastAPI(title="BIST Analiz GPT API")
mkk_id = pd.read_csv("mkkOId.csv",index_col="Unnamed: 0")

# Model sınıfı
class StockQuery(BaseModel):
    symbol: str

# Dummy veri (sonra gerçek veriyi buraya entegre edebilirsin)
stock_prices = {
    "THYAO": 275.4,
    "ASELS": 46.7,
    "KRDMD": 14.2
}

def get_news_list(from_date = "2025-03-28", to_date="2025-12-27", m_id="4028e4a140ee35c70140ee4e93870038"):    
    data = {
        "fromDate": from_date, "toDate": to_date,
        "year": "", "prd": "",
        "term": "", "ruleType": "",
        "bdkReview": "",
        "disclosureClass": "",#"DG",
        "index": "", "market": "",
        "mkkMemberOidList": [m_id],
        "inactiveMkkMemberOidList": [],
        "bdkMemberOidList": [],
        "mainSector": "", "sector": "",
        "subSector": "", "memberType": "IGS", #"DDK",
        "fromSrc": "false", "srcCategory": "",
        "discIndex": []}
    response = requests.post(url="https://www.kap.org.tr/tr/api/disclosure/members/byCriteria", json=data)
    return json.loads(response.text)

def extract_text_from_pdf_url(url):
    response = requests.get(url)
    response.raise_for_status()  # raise error if download fails

    # 3️⃣ Read PDF from memory
    pdf_file = io.BytesIO(response.content)

    # 4️⃣ Extract text
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text  # print first 1000 chars


def extract_and_save_announcement(series):
    disclosure_id = series["disclosureIndex"]
    url_kap = "https://www.kap.org.tr/tr/api/BildirimPdf/" + str(disclosure_id)
    series["accountmentText"] = extract_text_from_pdf_url(url_kap)
    time.sleep(2)
    return series

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
    mkk_stock_id = mkk_id.loc[query.symbol.upper()].values[0]
    news_df = pd.DataFrame(get_news_list(m_id=mkk_stock_id)[:5])
    if news_df is None:
        return {"symbol": query.symbol, "error": "KAP haberi bulunamadı"}
    news_df = news_df.apply(lambda x: extract_and_save_announcement(x),axis=1)
    return {"symbol": query.symbol.upper(), "news": {"columns": news_df.columns.tolist(),
    "data": news_df.fillna(0).to_dict(orient="records")
}}

# Test endpoint
@app.get("/")
def root():
    return {"message": "BIST Analiz GPT API çalışıyor!"}
