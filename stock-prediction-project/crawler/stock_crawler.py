import requests
import pandas as pd
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://finance.sina.com.cn/'
        }
    
    def get_stock_history(self, code, start_date=None, end_date=None):
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        try:
            market = 'sh' if code.startswith('6') else 'sz'
            url = f'https://quotes.sina.com.cn/cn/{market}{code}'
            
            df = self._fetch_from_sina(code, start_date, end_date)
            if df is not None and not df.empty:
                return df
            
            df = self._fetch_from_eastmoney(code, start_date, end_date)
            if df is not None and not df.empty:
                return df
            
            logger.warning(f"获取股票 {code} 历史数据失败")
            return None
        except Exception as e:
            logger.error(f"获取股票 {code} 历史数据异常: {str(e)}")
            return None
    
    def _fetch_from_sina(self, code, start_date, end_date):
        try:
            market = 'sh' if code.startswith('6') else 'sz'
            url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={market}{code}&scale=240&ma=no&datalen=500'
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    df = df[['day', 'open', 'high', 'low', 'close', 'volume']]
                    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                    df['date'] = pd.to_datetime(df['date'])
                    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)
                    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
                    logger.info(f"成功从新浪获取股票 {code} 历史数据")
                    return df
            return None
        except Exception as e:
            logger.error(f"从新浪获取股票 {code} 历史数据异常: {str(e)}")
            return None
    
    def _fetch_from_eastmoney(self, code, start_date, end_date):
        try:
            market = 1 if code.startswith('6') else 0
            url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={market}.{code}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg={start_date}&end={end_date}'
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get('klines'):
                    klines = data['data']['klines']
                    df = pd.DataFrame([line.split(',') for line in klines], 
                                     columns=['date', 'open', 'close', 'high', 'low', 'volume', 'amount'])
                    df['date'] = pd.to_datetime(df['date'])
                    df[['open', 'close', 'high', 'low', 'volume']] = df[['open', 'close', 'high', 'low', 'volume']].apply(pd.to_numeric)
                    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
                    logger.info(f"成功从东方财富获取股票 {code} 历史数据")
                    return df
            return None
        except Exception as e:
            logger.error(f"从东方财富获取股票 {code} 历史数据异常: {str(e)}")
            return None
    
    def get_stock_list(self, market='sh'):
        try:
            url = f'http://quote.eastmoney.com/{market}'
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.text, 'lxml')
            
            stock_list = []
            table = soup.find('table', {'id': 'table_wrapper-table'})
            if table:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        code = cells[0].text.strip()
                        name = cells[1].text.strip()
                        stock_list.append({'code': code, 'name': name})
            
            logger.info(f"成功获取{market}市场股票列表，共{len(stock_list)}只")
            return stock_list
        except Exception as e:
            logger.error(f"获取股票列表异常: {str(e)}")
            return []
    
    def get_realtime_price(self, code):
        try:
            url = f'http://qt.gtimg.cn/q=sh{code}' if code.startswith('6') else f'http://qt.gtimg.cn/q=sz{code}'
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.text.split('~')
                if len(data) >= 3:
                    return {
                        'code': code,
                        'name': data[1],
                        'price': float(data[3]),
                        'change': float(data[4]),
                        'change_percent': float(data[5]),
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            logger.warning(f"获取股票 {code} 实时价格失败")
            return None
        except Exception as e:
            logger.error(f"获取股票 {code} 实时价格异常: {str(e)}")
            return None