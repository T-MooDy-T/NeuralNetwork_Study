import pytest
import pandas as pd
import numpy as np
from ml_models.data_processor import DataProcessor

class TestDataProcessor:
    def setup_method(self):
        self.processor = DataProcessor()
        
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        self.df = pd.DataFrame({
            'date': dates,
            'open': np.random.uniform(100, 200, 100),
            'high': np.random.uniform(100, 200, 100),
            'low': np.random.uniform(100, 200, 100),
            'close': np.random.uniform(100, 200, 100),
            'volume': np.random.randint(10000, 1000000, 100)
        })
    
    def test_clean_data(self):
        result = self.processor.clean_data(self.df)
        assert len(result) == len(self.df)
    
    def test_create_features(self):
        result = self.processor.create_features(self.df)
        assert 'return' in result.columns
        assert 'ma5' in result.columns
        assert 'rsi' in result.columns
    
    def test_normalize_data(self):
        result = self.processor.normalize_data(self.df)
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            assert result[col].min() >= 0
            assert result[col].max() <= 1
    
    def test_create_time_series_data(self):
        df_features = self.processor.create_features(self.df)
        X, y = self.processor.create_time_series_data(df_features, look_back=60)
        assert X.shape[0] == y.shape[0]
        assert X.shape[1] == 60
    
    def test_split_data(self):
        df_features = self.processor.create_features(self.df)
        X, y = self.processor.create_time_series_data(df_features, look_back=60)
        X_train, X_test, y_train, y_test = self.processor.split_data(X, y)
        assert len(X_train) > len(X_test)