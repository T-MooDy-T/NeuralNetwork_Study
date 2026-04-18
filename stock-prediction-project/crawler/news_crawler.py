import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://guba.eastmoney.com/'
        }
    
    def get_stock_news(self, code, limit=20):
        try:
            market = 1 if code.startswith('6') else 0
            url = f'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz={limit}&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f62&fs=m:{market}+t:{code}&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f23,f24,f25,f26,f22,f33,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f23,f24,f25,f26,f22,f33'
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get('diff'):
                    news_list = []
                    for item in data['data']['diff'][:limit]:
                        news = {
                            'title': item.get('f14', ''),
                            'url': f'http://guba.eastmoney.com/news/{code},{item.get("f12", "")}.html',
                            'time': item.get('f57', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                            'code': code
                        }
                        news_list.append(news)
                    
                    logger.info(f"成功获取股票 {code} 新闻资讯，共{len(news_list)}条")
                    return news_list
            
            return self._get_stock_news_backup(code, limit)
        except Exception as e:
            logger.error(f"获取股票 {code} 新闻资讯异常: {str(e)}")
            return self._get_stock_news_backup(code, limit)
    
    def _get_stock_news_backup(self, code, limit=20):
        try:
            url = f'http://guba.eastmoney.com/list,{code}_1.html'
            response = requests.get(url, headers=self.headers, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                news_list = []
                
                items = soup.find_all('div', {'class': 'articleh'})[:limit]
                for item in items:
                    title_tag = item.find('a')
                    time_tag = item.find('span', {'class': 'l5'})
                    
                    if title_tag:
                        news = {
                            'title': title_tag.text.strip(),
                            'url': 'http://guba.eastmoney.com' + title_tag['href'],
                            'time': time_tag.text.strip() if time_tag else datetime.now().strftime('%Y-%m-%d'),
                            'code': code
                        }
                        news_list.append(news)
                
                logger.info(f"成功获取股票 {code} 新闻资讯(备用)，共{len(news_list)}条")
                return news_list
            
            logger.warning(f"获取股票 {code} 新闻资讯失败")
            return []
        except Exception as e:
            logger.error(f"获取股票 {code} 新闻资讯(备用)异常: {str(e)}")
            return []
    
    def get_financial_news(self, limit=30):
        try:
            url = 'https://news.eastmoney.com/'
            response = requests.get(url, headers=self.headers, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                news_list = []
                
                items = soup.find_all('div', {'class': 'newsItem'})[:limit]
                for item in items:
                    title_tag = item.find('a')
                    time_tag = item.find('span', {'class': 'time'})
                    
                    if title_tag:
                        news = {
                            'title': title_tag.text.strip(),
                            'url': title_tag['href'] if 'http' in title_tag['href'] else 'http://news.eastmoney.com' + title_tag['href'],
                            'time': time_tag.text.strip() if time_tag else datetime.now().strftime('%Y-%m-%d'),
                            'category': '财经新闻'
                        }
                        news_list.append(news)
                
                logger.info(f"成功获取财经新闻，共{len(news_list)}条")
                return news_list
            
            logger.warning("获取财经新闻失败")
            return []
        except Exception as e:
            logger.error(f"获取财经新闻异常: {str(e)}")
            return []
    
    def get_industry_news(self, industry, limit=20):
        try:
            url = f'http://industry.eastmoney.com/{industry}'
            response = requests.get(url, headers=self.headers, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                news_list = []
                
                items = soup.find_all('div', {'class': 'news_list'})
                for item in items[:limit]:
                    title_tag = item.find('a')
                    time_tag = item.find('span')
                    
                    if title_tag:
                        news = {
                            'title': title_tag.text.strip(),
                            'url': title_tag['href'],
                            'time': time_tag.text.strip() if time_tag else datetime.now().strftime('%Y-%m-%d'),
                            'industry': industry
                        }
                        news_list.append(news)
                
                logger.info(f"成功获取{industry}行业新闻，共{len(news_list)}条")
                return news_list
            
            logger.warning(f"获取{industry}行业新闻失败")
            return []
        except Exception as e:
            logger.error(f"获取{industry}行业新闻异常: {str(e)}")
            return []