from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.db_utils import DBUtils
from crawler.stock_crawler import StockCrawler

router = APIRouter()
crawler = StockCrawler()

from typing import Optional

def get_db():
    return DBUtils()

class StockResponse(BaseModel):
    id: int
    code: str
    name: str
    industry: Optional[str] = None
    market: Optional[str] = None

class DailyDataResponse(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

@router.get("/", response_model=list[StockResponse])
async def get_stock_list():
    try:
        import numpy as np
        db = get_db()
        df = db.get_stock_list()
        db.close()
        records = df.to_dict('records')
        for record in records:
            for key, value in record.items():
                if isinstance(value, float) and np.isnan(value):
                    record[key] = None
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}")
async def get_stock_info(code: str):
    try:
        db = get_db()
        stock_id = db.get_stock_id(code)
        if not stock_id:
            db.close()
            raise HTTPException(status_code=404, detail="Stock not found")
        
        df = db.get_stock_list()
        stock = df[df['code'] == code].iloc[0].to_dict()
        db.close()
        return stock
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}/history", response_model=list[DailyDataResponse])
async def get_stock_history(code: str, start_date: str = None, end_date: str = None):
    try:
        db = get_db()
        stock_id = db.get_stock_id(code)
        if not stock_id:
            db.close()
            raise HTTPException(status_code=404, detail="Stock not found")
        
        df = db.get_daily_data(stock_id, start_date, end_date)
        db.close()
        return df.to_dict('records')
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}/realtime")
async def get_realtime_price(code: str):
    try:
        data = crawler.get_realtime_price(code)
        if not data:
            raise HTTPException(status_code=404, detail="Failed to get realtime price")
        return data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{code}/update")
async def update_stock_data(code: str):
    try:
        db = get_db()
        stock_id = db.get_stock_id(code)
        if not stock_id:
            db.close()
            raise HTTPException(status_code=404, detail="Stock not found")
        
        df = crawler.get_stock_history(code)
        if df is not None:
            for _, row in df.iterrows():
                db.insert_daily_data(
                    stock_id=stock_id,
                    date=row['date'].strftime('%Y-%m-%d'),
                    open_price=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=int(row['volume'])
                )
            db.close()
            return {"message": f"Successfully updated {len(df)} records"}
        else:
            db.close()
            raise HTTPException(status_code=500, detail="Failed to fetch data")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add")
async def add_stock(code: str):
    try:
        realtime = crawler.get_realtime_price(code)
        if not realtime:
            raise HTTPException(status_code=404, detail="Failed to get stock info")
        
        market = 'sh' if code.startswith('6') else 'sz'
        db = get_db()
        stock_id = db.insert_stock(
            code=code,
            name=realtime['name'],
            market=market
        )
        
        if stock_id:
            df = crawler.get_stock_history(code)
            if df is not None:
                for _, row in df.iterrows():
                    db.insert_daily_data(
                        stock_id=stock_id,
                        date=row['date'].strftime('%Y-%m-%d'),
                        open_price=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=int(row['volume'])
                    )
            
            db.close()
            return {
                "message": f"Stock {code} ({realtime['name']}) added successfully",
                "stock": {
                    "id": stock_id,
                    "code": code,
                    "name": realtime['name'],
                    "market": market
                }
            }
        else:
            db.close()
            raise HTTPException(status_code=500, detail="Failed to add stock")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))