import pandas as pd
import logging
import pymysql
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBUtils:
    def __init__(self, db_type='mysql'):
        self.db_type = db_type
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        try:
            if self.db_type == 'mysql':
                self.conn = pymysql.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=int(os.getenv('DB_PORT', 3306)),
                    user=os.getenv('DB_USER', 'root'),
                    password=os.getenv('DB_PASSWORD', ''),
                    database=os.getenv('DB_NAME', 'stock_prediction'),
                    charset='utf8mb4',
                    use_unicode=True
                )
            else:
                import sqlite3
                self.conn = sqlite3.connect('stock_data.db')
            
            logger.info(f"成功连接{self.db_type}数据库")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise
    
    def create_tables(self):
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    code VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    industry VARCHAR(100),
                    market VARCHAR(20),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_data (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    stock_id INT,
                    date DATE NOT NULL,
                    open DECIMAL(10,2),
                    high DECIMAL(10,2),
                    low DECIMAL(10,2),
                    close DECIMAL(10,2),
                    volume BIGINT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_id) REFERENCES stocks(id),
                    UNIQUE(stock_id, date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_data (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    stock_id INT,
                    report_date DATE NOT NULL,
                    eps DECIMAL(10,4),
                    pe DECIMAL(10,2),
                    pb DECIMAL(10,2),
                    revenue DECIMAL(18,2),
                    net_profit DECIMAL(18,2),
                    roe DECIMAL(10,4),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_id) REFERENCES stocks(id),
                    UNIQUE(stock_id, report_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    stock_id INT,
                    title VARCHAR(500) NOT NULL,
                    url VARCHAR(1000),
                    content TEXT,
                    publish_time DATETIME,
                    sentiment DECIMAL(5,2),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_id) REFERENCES stocks(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    stock_id INT,
                    prediction_date DATE NOT NULL,
                    predicted_price DECIMAL(10,2),
                    lower_bound DECIMAL(10,2),
                    upper_bound DECIMAL(10,2),
                    confidence DECIMAL(5,2),
                    model_type VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_id) REFERENCES stocks(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            self.conn.commit()
            logger.info("数据库表创建完成")
        except Exception as e:
            logger.error(f"创建表失败: {str(e)}")
            self.conn.rollback()
    
    def insert_stock(self, code, name, industry=None, market=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO stocks (code, name, industry, market)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=VALUES(name), industry=VALUES(industry), market=VALUES(market)
            ''', (code, name, industry, market))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入股票失败: {str(e)}")
            self.conn.rollback()
            return None
    
    def insert_daily_data(self, stock_id, date, open_price, high, low, close, volume):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO daily_data 
                (stock_id, date, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE open=VALUES(open), high=VALUES(high), low=VALUES(low), close=VALUES(close), volume=VALUES(volume)
            ''', (stock_id, date, open_price, high, low, close, volume))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入日数据失败: {str(e)}")
            self.conn.rollback()
            return None
    
    def insert_financial_data(self, stock_id, report_date, eps=None, pe=None, pb=None, revenue=None, net_profit=None, roe=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO financial_data 
                (stock_id, report_date, eps, pe, pb, revenue, net_profit, roe)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE eps=VALUES(eps), pe=VALUES(pe), pb=VALUES(pb), revenue=VALUES(revenue), net_profit=VALUES(net_profit), roe=VALUES(roe)
            ''', (stock_id, report_date, eps, pe, pb, revenue, net_profit, roe))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入财务数据失败: {str(e)}")
            self.conn.rollback()
            return None
    
    def insert_news(self, stock_id, title, url, content=None, publish_time=None, sentiment=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO news (stock_id, title, url, content, publish_time, sentiment)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (stock_id, title, url, content, publish_time, sentiment))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入新闻失败: {str(e)}")
            self.conn.rollback()
            return None
    
    def insert_prediction(self, stock_id, prediction_date, predicted_price, lower_bound=None, upper_bound=None, confidence=None, model_type='lstm'):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (stock_id, prediction_date, predicted_price, lower_bound, upper_bound, confidence, model_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (stock_id, prediction_date, predicted_price, lower_bound, upper_bound, confidence, model_type))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入预测数据失败: {str(e)}")
            self.conn.rollback()
            return None
    
    def get_stock_id(self, code):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM stocks WHERE code = %s', (code,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"获取股票ID失败: {str(e)}")
            return None
    
    def get_stock_list(self):
        try:
            df = pd.read_sql('SELECT * FROM stocks', self.conn)
            df = df.where(pd.notna(df), None)
            return df
        except Exception as e:
            logger.error(f"获取股票列表失败: {str(e)}")
            return pd.DataFrame()
    
    def get_daily_data(self, stock_id, start_date=None, end_date=None):
        try:
            query = 'SELECT * FROM daily_data WHERE stock_id = %s'
            params = [stock_id]
            
            if start_date:
                query += ' AND date >= %s'
                params.append(start_date)
            if end_date:
                query += ' AND date <= %s'
                params.append(end_date)
            
            query += ' ORDER BY date ASC'
            df = pd.read_sql(query, self.conn, params=params)
            
            if not df.empty and 'date' in df.columns:
                df['date'] = df['date'].astype(str)
            
            return df
        except Exception as e:
            logger.error(f"获取日数据失败: {str(e)}")
            return pd.DataFrame()
    
    def get_financial_data(self, stock_id):
        try:
            df = pd.read_sql('SELECT * FROM financial_data WHERE stock_id = %s ORDER BY report_date DESC', self.conn, params=[stock_id])
            return df
        except Exception as e:
            logger.error(f"获取财务数据失败: {str(e)}")
            return pd.DataFrame()
    
    def get_news(self, stock_id, limit=20):
        try:
            df = pd.read_sql('SELECT * FROM news WHERE stock_id = %s ORDER BY publish_time DESC LIMIT %s', self.conn, params=[stock_id, limit])
            return df
        except Exception as e:
            logger.error(f"获取新闻失败: {str(e)}")
            return pd.DataFrame()
    
    def get_predictions(self, stock_id):
        try:
            df = pd.read_sql('SELECT * FROM predictions WHERE stock_id = %s ORDER BY prediction_date ASC', self.conn, params=[stock_id])
            return df
        except Exception as e:
            logger.error(f"获取预测数据失败: {str(e)}")
            return pd.DataFrame()
    
    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")