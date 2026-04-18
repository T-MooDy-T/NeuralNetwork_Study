# -*- coding: utf-8 -*-
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def reinit_database():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            charset='utf8mb4',
            use_unicode=True
        )
        
        cursor = connection.cursor()
        
        cursor.execute(f"DROP DATABASE IF EXISTS {os.getenv('DB_NAME', 'stock_prediction')}")
        cursor.execute(f"CREATE DATABASE {os.getenv('DB_NAME', 'stock_prediction')} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {os.getenv('DB_NAME', 'stock_prediction')}")
        
        cursor.execute('SET NAMES utf8mb4')
        cursor.execute('SET CHARACTER SET utf8mb4')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INT PRIMARY KEY AUTO_INCREMENT,
                code VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                industry VARCHAR(100),
                market VARCHAR(20),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        sample_stocks = [
            ('600519', '贵州茅台', '白酒', 'sh'),
            ('000858', '五粮液', '白酒', 'sz'),
            ('000651', '格力电器', '家电', 'sz'),
            ('601318', '中国平安', '保险', 'sh'),
            ('000001', '平安银行', '银行', 'sz'),
            ('600036', '招商银行', '银行', 'sh')
        ]
        
        for code, name, industry, market in sample_stocks:
            cursor.execute('''
                INSERT INTO stocks (code, name, industry, market)
                VALUES (%s, %s, %s, %s)
            ''', (code, name, industry, market))
        
        connection.commit()
        print("Database reinitialized successfully!")
        
        cursor.execute('SELECT code, name FROM stocks')
        results = cursor.fetchall()
        print("\nInserted stocks:")
        for row in results:
            print(f"  {row[0]} - {row[1]}")
        
        connection.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    reinit_database()