from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.db_utils import DBUtils
from crawler.news_crawler import NewsCrawler

router = APIRouter()
crawler = NewsCrawler()

def get_db():
    return DBUtils()

class NewsResponse(BaseModel):
    title: str
    url: str
    publish_time: str = None
    sentiment: float = None

@router.get("/{code}", response_model=list[NewsResponse])
async def get_stock_news(code: str, limit: int = 20):
    try:
        db = get_db()
        stock_id = db.get_stock_id(code)
        if not stock_id:
            db.close()
            raise HTTPException(status_code=404, detail="Stock not found")
        
        df = db.get_news(stock_id, limit=limit)
        db.close()
        return df.to_dict('records')
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/general")
async def get_general_news(limit: int = 30):
    try:
        news = crawler.get_financial_news(limit=limit)
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{code}/update")
async def update_stock_news(code: str):
    try:
        db = get_db()
        stock_id = db.get_stock_id(code)
        if not stock_id:
            db.close()
            raise HTTPException(status_code=404, detail="Stock not found")
        
        news_list = crawler.get_stock_news(code, limit=20)
        for news in news_list:
            db.insert_news(
                stock_id=stock_id,
                title=news['title'],
                url=news['url'],
                publish_time=news['time']
            )
        db.close()
        return {"message": f"Successfully updated {len(news_list)} news items"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))