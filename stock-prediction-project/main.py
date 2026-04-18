import argparse
import logging
from utils.logger import setup_logger
from utils.db_utils import DBUtils
from crawler.stock_crawler import StockCrawler
from crawler.finance_crawler import FinanceCrawler
from crawler.news_crawler import NewsCrawler
from ml_models.data_processor import DataProcessor
from ml_models.model_trainer import ModelTrainer
from ml_models.predictor import Predictor
import pandas as pd

logger = setup_logger()

def init_stocks(db, codes):
    crawler = StockCrawler()
    
    for code in codes:
        try:
            stock_data = crawler.get_realtime_price(code)
            if stock_data:
                db.insert_stock(
                    code=code,
                    name=stock_data['name'],
                    market='sh' if code.startswith('6') else 'sz'
                )
                logger.info(f"Added stock: {code} - {stock_data['name']}")
        except Exception as e:
            logger.error(f"Failed to add stock {code}: {str(e)}")

def fetch_data(db, code):
    stock_id = db.get_stock_id(code)
    if not stock_id:
        logger.error(f"Stock {code} not found in database")
        return
    
    stock_crawler = StockCrawler()
    finance_crawler = FinanceCrawler()
    news_crawler = NewsCrawler()
    
    logger.info(f"Fetching daily data for {code}")
    df = stock_crawler.get_stock_history(code)
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
    
    logger.info(f"Fetching financial data for {code}")
    indicators = finance_crawler.get_indicators(code)
    if indicators:
        db.insert_financial_data(
            stock_id=stock_id,
            report_date='2024-12-31',
            eps=float(indicators.get('每股收益', 0)),
            pe=float(indicators.get('市盈率', 0)),
            pb=float(indicators.get('市净率', 0)),
            roe=float(indicators.get('净资产收益率', 0))
        )
    
    logger.info(f"Fetching news for {code}")
    news_list = news_crawler.get_stock_news(code, limit=10)
    for news in news_list:
        db.insert_news(
            stock_id=stock_id,
            title=news['title'],
            url=news['url'],
            publish_time=news['time']
        )

def train_model(db, code):
    stock_id = db.get_stock_id(code)
    if not stock_id:
        logger.error(f"Stock {code} not found in database")
        return
    
    df = db.get_daily_data(stock_id)
    if df.empty:
        logger.error(f"No data found for stock {code}")
        return
    
    processor = DataProcessor()
    df_clean = processor.clean_data(df)
    df_features = processor.create_features(df_clean)
    
    numeric_cols = df_features.select_dtypes(include=['float64', 'int64']).columns
    df_normalized = processor.normalize_data(df_features, columns=numeric_cols)
    
    X, y = processor.create_time_series_data(df_normalized, look_back=60)
    X_train, X_test, y_train, y_test = processor.split_data(X, y)
    
    trainer = ModelTrainer()
    model, history = trainer.train_lstm(
        X_train, y_train,
        X_val=X_test, y_val=y_test,
        epochs=50,
        batch_size=32
    )
    
    metrics = trainer.evaluate_model(model, X_test, y_test, model_type='lstm')
    logger.info(f"Model evaluation metrics: {metrics}")
    
    trainer.save_model(model, 'lstm_model')
    logger.info("Model training completed and saved")

def run_backend():
    import uvicorn
    from web.backend.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    parser = argparse.ArgumentParser(description="Stock Prediction Project")
    parser.add_argument('--init', nargs='+', help='Initialize stocks with given codes')
    parser.add_argument('--fetch', help='Fetch data for a specific stock')
    parser.add_argument('--train', help='Train model for a specific stock')
    parser.add_argument('--backend', action='store_true', help='Run the FastAPI backend')
    
    args = parser.parse_args()
    
    db = DBUtils()
    
    if args.init:
        init_stocks(db, args.init)
    elif args.fetch:
        fetch_data(db, args.fetch)
    elif args.train:
        train_model(db, args.train)
    elif args.backend:
        run_backend()
    else:
        parser.print_help()
    
    db.close()

if __name__ == "__main__":
    main()