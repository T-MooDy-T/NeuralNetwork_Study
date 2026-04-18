from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.db_utils import DBUtils
from ml_models.predictor import Predictor
from ml_models.data_processor import DataProcessor
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import os
import glob

router = APIRouter()

def get_db():
    return DBUtils()

def find_latest_model(model_prefix='lstm_model'):
    model_pattern = f'models/{model_prefix}*.h5'
    models = glob.glob(model_pattern)
    if not models:
        return None
    models.sort(key=os.path.getmtime, reverse=True)
    return models[0]

class PredictionRequest(BaseModel):
    code: str
    days: int = 7

class PredictionResponse(BaseModel):
    code: str
    date: str
    predicted_price: float
    lower_bound: float = None
    upper_bound: float = None
    confidence: float = None

def calculate_atr(df, window=14):
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    atr = tr.rolling(window=window).mean()
    return atr

def add_additional_features(df):
    df = df.copy()
    
    df['price_to_ma5'] = df['close'] / df['ma5']
    df['price_to_ma20'] = df['close'] / df['ma20']
    df['price_to_ma60'] = df['close'] / df['close'].rolling(window=60).mean()
    
    df['volume_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume_ratio'].fillna(1)
    
    df['volatility'] = df['std10'] / df['close']
    
    df['momentum'] = df['close'].pct_change(5)
    df['momentum_20'] = df['close'].pct_change(20)
    
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
    
    df['macd_signal'] = (df['macd'] > df['signal']).astype(int)
    
    df['day_of_week_sin'] = np.sin(2 * np.pi * df['date'].dt.dayofweek / 5)
    df['day_of_week_cos'] = np.cos(2 * np.pi * df['date'].dt.dayofweek / 5)
    df['month_sin'] = np.sin(2 * np.pi * df['date'].dt.month / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['date'].dt.month / 12)
    
    df['atr'] = calculate_atr(df)
    df['atr_ratio'] = df['atr'] / df['close']
    
    df['return_volatility_ratio'] = df['return'] / df['volatility']
    df['volume_ma_ratio'] = df['volume'] / df['volume'].rolling(window=5).mean()
    
    df['high_low_ratio'] = df['high'] / df['low']
    df['close_open_ratio'] = df['close'] / df['open']
    
    return df

@router.post("/", response_model=list[PredictionResponse])
async def create_prediction(request: PredictionRequest):
    try:
        db = get_db()
        stock_id = db.get_stock_id(request.code)
        if not stock_id:
            db.close()
            raise HTTPException(status_code=404, detail="Stock not found")
        
        df = db.get_daily_data(stock_id)
        if df.empty:
            db.close()
            raise HTTPException(status_code=404, detail="No historical data found")
        
        df = df.sort_values('date')
        
        if len(df) < 60:
            db.close()
            raise HTTPException(status_code=400, detail=f"Insufficient historical data. Need at least 60 days, but only have {len(df)} days.")
        
        df['date'] = pd.to_datetime(df['date'])
        
        processor = DataProcessor()
        df_processed = processor.clean_data(df)
        df_processed = processor.create_features(df_processed)
        df_processed = add_additional_features(df_processed)
        df_processed = df_processed.dropna()
        
        numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != 'id']
        df_normalized = processor.normalize_data(df_processed, columns=numeric_cols)
        
        look_back = min(60, len(df_processed) - 1)
        X, _ = processor.create_time_series_data(df_normalized, look_back=look_back)
        
        model_path = find_latest_model('lstm_model')
        if not model_path:
            db.close()
            raise HTTPException(status_code=503, detail="Model not trained yet")
        
        try:
            model = load_model(model_path)
        except Exception as e:
            db.close()
            raise HTTPException(status_code=503, detail=f"Failed to load model: {str(e)}")
        
        scaler = processor.scaler
        predictor = Predictor(model, scaler)
        
        last_date = df['date'].iloc[-1]
        dates = predictor.generate_prediction_dates(last_date, days=request.days)
        
        X_input = X[-1].reshape(1, look_back, X.shape[2])
        predictions = predictor.predict_multiple_days(X_input, days=len(dates))
        
        close_min = df['close'].min()
        close_max = df['close'].max()
        denorm_predictions = [predictor.denormalize_prediction(p, close_min, close_max) for p in predictions]
        
        results = []
        for date, pred in zip(dates, denorm_predictions):
            db.insert_prediction(
                stock_id=stock_id,
                prediction_date=date,
                predicted_price=pred,
                model_type='lstm'
            )
            results.append({
                'code': request.code,
                'date': date,
                'predicted_price': pred
            })
        
        db.close()
        return results
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}", response_model=list[PredictionResponse])
async def get_predictions(code: str):
    try:
        db = get_db()
        stock_id = db.get_stock_id(code)
        if not stock_id:
            db.close()
            raise HTTPException(status_code=404, detail="Stock not found")
        
        df = db.get_predictions(stock_id)
        db.close()
        return df.to_dict('records')
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))