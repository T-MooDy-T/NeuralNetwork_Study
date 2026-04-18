from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from utils.db_utils import DBUtils
from crawler.finance_crawler import FinanceCrawler

router = APIRouter()
crawler = FinanceCrawler()

def get_db():
    return DBUtils()

class FinancialResponse(BaseModel):
    report_date: str
    eps: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    revenue: Optional[float] = None
    net_profit: Optional[float] = None
    roe: Optional[float] = None

@router.get("/{code}", response_model=list[FinancialResponse])
async def get_financial_data(code: str):
    try:
        db = get_db()
        stock_id = db.get_stock_id(code)
        if not stock_id:
            db.close()
            raise HTTPException(status_code=404, detail="Stock not found")
        
        df = db.get_financial_data(stock_id)
        if not df.empty:
            db.close()
            return df.to_dict('records')
        
        db.close()
        indicators = crawler.get_indicators(code)
        if indicators:
            return [{
                "report_date": "2024-12-31",
                "eps": float(indicators.get('每股收益', 0)) if indicators.get('每股收益') else None,
                "pe": float(indicators.get('市盈率', 0)) if indicators.get('市盈率') else None,
                "pb": float(indicators.get('市净率', 0)) if indicators.get('市净率') else None,
                "revenue": None,
                "net_profit": None,
                "roe": float(indicators.get('净资产收益率', 0)) if indicators.get('净资产收益率') else None
            }]
        
        return [{
            "report_date": "2024-12-31",
            "eps": None,
            "pe": None,
            "pb": None,
            "revenue": None,
            "net_profit": None,
            "roe": None
        }]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}/indicators")
async def get_financial_indicators(code: str):
    try:
        indicators = crawler.get_indicators(code)
        if not indicators:
            raise HTTPException(status_code=404, detail="Failed to get indicators")
        return indicators
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{code}/update")
async def update_financial_data(code: str):
    try:
        db = get_db()
        stock_id = db.get_stock_id(code)
        if not stock_id:
            db.close()
            raise HTTPException(status_code=404, detail="Stock not found")
        
        indicators = crawler.get_indicators(code)
        if indicators:
            db.insert_financial_data(
                stock_id=stock_id,
                report_date='2024-12-31',
                eps=float(indicators.get('每股收益', 0)),
                pe=float(indicators.get('市盈率', 0)),
                pb=float(indicators.get('市净率', 0)),
                roe=float(indicators.get('净资产收益率', 0))
            )
            db.close()
            return {"message": "Financial data updated successfully"}
        else:
            db.close()
            raise HTTPException(status_code=500, detail="Failed to fetch financial data")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))