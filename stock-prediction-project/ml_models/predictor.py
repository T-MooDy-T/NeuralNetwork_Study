import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Predictor:
    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler
    
    def predict_next_day(self, X):
        try:
            prediction = self.model.predict(X)
            return prediction[0][0] if len(prediction.shape) > 1 else prediction[0]
        except Exception as e:
            logger.error(f"单日预测异常: {str(e)}")
            return None
    
    def predict_multiple_days(self, X, days=7):
        predictions = []
        current_data = X.copy()
        
        try:
            for i in range(days):
                prediction = self.model.predict(current_data)
                
                if len(prediction.shape) > 1:
                    pred_value = prediction[0][0]
                else:
                    pred_value = prediction[0]
                
                predictions.append(pred_value)
                
                if current_data.ndim == 3:
                    new_row = np.zeros((1, 1, current_data.shape[2]))
                    new_row[0, 0, 0] = pred_value
                    current_data = np.concatenate([current_data[:, 1:, :], new_row], axis=1)
                else:
                    current_data = np.roll(current_data, -1)
                    current_data[-1] = pred_value
            
            logger.info(f"多日预测完成，预测天数: {days}")
            return predictions
        except Exception as e:
            logger.error(f"多日预测异常: {str(e)}")
            return []
    
    def predict_with_confidence(self, X, n_simulations=100):
        predictions = []
        
        try:
            for _ in range(n_simulations):
                pred = self.model.predict(X)
                predictions.append(pred[0][0] if len(pred.shape) > 1 else pred[0])
            
            mean_pred = np.mean(predictions)
            std_pred = np.std(predictions)
            lower_bound = mean_pred - 1.96 * std_pred
            upper_bound = mean_pred + 1.96 * std_pred
            
            result = {
                'prediction': mean_pred,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'confidence': 0.95,
                'std': std_pred
            }
            
            logger.info(f"带置信区间预测完成")
            return result
        except Exception as e:
            logger.error(f"置信区间预测异常: {str(e)}")
            return None
    
    def denormalize_prediction(self, prediction, original_min, original_max):
        return prediction * (original_max - original_min) + original_min
    
    def generate_prediction_dates(self, last_date, days=7):
        dates = []
        current_date = datetime.strptime(last_date, '%Y-%m-%d') if isinstance(last_date, str) else last_date
        
        for i in range(1, days + 1):
            next_date = current_date + timedelta(days=i)
            if next_date.weekday() < 5:
                dates.append(next_date.strftime('%Y-%m-%d'))
        
        return dates
    
    def create_prediction_df(self, dates, predictions):
        df = pd.DataFrame({
            'date': dates,
            'predicted_close': predictions,
            'type': 'prediction'
        })
        return df