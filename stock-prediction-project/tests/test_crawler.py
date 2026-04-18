import pytest
from crawler.stock_crawler import StockCrawler
from crawler.finance_crawler import FinanceCrawler
from crawler.news_crawler import NewsCrawler

class TestStockCrawler:
    def setup_method(self):
        self.crawler = StockCrawler()
    
    def test_get_realtime_price(self):
        result = self.crawler.get_realtime_price('600519')
        assert result is not None
        assert 'code' in result
        assert 'price' in result
    
    def test_get_stock_list(self):
        result = self.crawler.get_stock_list('sh')
        assert isinstance(result, list)
        assert len(result) > 0

class TestFinanceCrawler:
    def setup_method(self):
        self.crawler = FinanceCrawler()
    
    def test_get_indicators(self):
        result = self.crawler.get_indicators('600519')
        assert result is not None
        assert isinstance(result, dict)

class TestNewsCrawler:
    def setup_method(self):
        self.crawler = NewsCrawler()
    
    def test_get_stock_news(self):
        result = self.crawler.get_stock_news('600519')
        assert isinstance(result, list)
    
    def test_get_financial_news(self):
        result = self.crawler.get_financial_news()
        assert isinstance(result, list)
        assert len(result) > 0