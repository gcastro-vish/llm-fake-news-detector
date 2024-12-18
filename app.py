from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Union

from src.analysis import make_analysis

app = FastAPI()

class AnalyzeRequest(BaseModel):
    article: str
    headline: str

@app.get("/")
async def root():
    return {"Message": "Server is up and runnnig!"}

@app.post("/v1/analyze/")
async def analyze_fake_news(request: AnalyzeRequest) -> Dict[str, Union[int, str]]:
    try:
        return await make_analysis(headline=request.headline, article=request.article)
    except Exception as e:
        return {"error": str(e)}