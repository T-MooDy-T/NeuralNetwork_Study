from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import stocks, predictions, financial, news

app = FastAPI(title="Stock Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(financial.router, prefix="/api/financial", tags=["financial"])
app.include_router(news.router, prefix="/api/news", tags=["news"])

@app.get("/")
async def root():
    return {"message": "Stock Prediction API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}