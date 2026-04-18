import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_regression
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.imputer = SimpleImputer(strategy='mean')
    
    def clean_data(self, df):
        df = df.copy()
        
        df = df.drop_duplicates()
        
        df = df.dropna(subset=['date', 'close'])
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = self.imputer.fit_transform(df[numeric_cols])
        
        logger.info("数据清洗完成")
        return df
    
    def create_features(self, df):
        df = df.copy()
        
        df['return'] = df['close'].pct_change()
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        
        for i in range(1, 6):
            df[f'close_lag_{i}'] = df['close'].shift(i)
            df[f'volume_lag_{i}'] = df['volume'].shift(i)
        
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        
        df['std5'] = df['close'].rolling(window=5).std()
        df['std10'] = df['close'].rolling(window=10).std()
        
        df['upper_band'] = df['ma20'] + 2 * df['std10']
        df['lower_band'] = df['ma20'] - 2 * df['std10']
        
        df['rsi'] = self.calculate_rsi(df['close'], window=14)
        
        df['macd'], df['signal'], df['hist'] = self.calculate_macd(df['close'])
        
        df = df.dropna()
        
        logger.info("特征工程完成")
        return df
    
    def calculate_rsi(self, prices, window=14):
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return macd, signal_line, histogram
    
    def normalize_data(self, df, columns=None):
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns
        
        df = df.copy()
        df[columns] = self.scaler.fit_transform(df[columns])
        
        logger.info("数据标准化完成")
        return df
    
    def create_time_series_data(self, df, target_col='close', look_back=60):
        numeric_df = df.select_dtypes(include=[np.number])
        data = numeric_df.values.astype(np.float32)
        X, y = [], []
        
        target_idx = numeric_df.columns.get_loc(target_col)
        
        for i in range(look_back, len(data)):
            X.append(data[i-look_back:i, :])
            y.append(data[i, target_idx])
        
        X, y = np.array(X), np.array(y)
        
        logger.info(f"时间序列数据创建完成，样本数: {len(X)}")
        return X, y
    
    def split_data(self, X, y, train_ratio=0.8):
        train_size = int(len(X) * train_ratio)
        
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        logger.info(f"数据划分完成，训练集: {len(X_train)}, 测试集: {len(X_test)}")
        return X_train, X_test, y_train, y_test
    
    def select_features(self, X, y, k=10):
        selector = SelectKBest(f_regression, k=k)
        X_selected = selector.fit_transform(X.reshape(X.shape[0], -1), y)
        
        logger.info(f"特征选择完成，保留 {k} 个特征")
        return X_selected, selector