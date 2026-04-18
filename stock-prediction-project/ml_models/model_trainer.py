import numpy as np
import pandas as pd
import logging
from datetime import datetime
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, MultiHeadAttention, LayerNormalization, GlobalAveragePooling1D
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.models = {}
    
    def build_lstm_model(self, input_shape):
        model = Sequential()
        model.add(LSTM(units=128, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(units=64, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=32, activation='relu'))
        model.add(Dense(units=1))
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        return model
    
    def build_transformer_model(self, input_shape):
        inputs = Input(shape=input_shape)
        
        x = inputs
        for _ in range(2):
            attn_output = MultiHeadAttention(num_heads=4, key_dim=input_shape[-1])(x, x)
            x = LayerNormalization(epsilon=1e-6)(x + attn_output)
            
            ff_output = Dense(input_shape[-1], activation='relu')(x)
            ff_output = Dense(input_shape[-1])(ff_output)
            x = LayerNormalization(epsilon=1e-6)(x + ff_output)
        
        x = GlobalAveragePooling1D()(x)
        x = Dense(64, activation='relu')(x)
        outputs = Dense(1)(x)
        
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        return model
    
    def build_xgboost_model(self):
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective='reg:squarederror',
            random_state=42
        )
        return model
    
    def build_lightgbm_model(self):
        model = lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective='regression',
            random_state=42
        )
        return model
    
    def train_lstm(self, X_train, y_train, X_val=None, y_val=None, epochs=100, batch_size=32):
        input_shape = (X_train.shape[1], X_train.shape[2])
        model = self.build_lstm_model(input_shape)
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ModelCheckpoint(f'models/lstm_model_{datetime.now().strftime("%Y%m%d")}.h5', save_best_only=True)
        ]
        
        if X_val is not None and y_val is not None:
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks
            )
        else:
            history = model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.1,
                callbacks=callbacks
            )
        
        self.models['lstm'] = model
        logger.info("LSTM模型训练完成")
        return model, history
    
    def train_transformer(self, X_train, y_train, X_val=None, y_val=None, epochs=50, batch_size=32):
        input_shape = (X_train.shape[1], X_train.shape[2])
        model = self.build_transformer_model(input_shape)
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ModelCheckpoint(f'models/transformer_model_{datetime.now().strftime("%Y%m%d")}.h5', save_best_only=True)
        ]
        
        if X_val is not None and y_val is not None:
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks
            )
        else:
            history = model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.1,
                callbacks=callbacks
            )
        
        self.models['transformer'] = model
        logger.info("Transformer模型训练完成")
        return model, history
    
    def train_xgboost(self, X_train, y_train, X_val=None, y_val=None):
        model = self.build_xgboost_model()
        
        if X_val is not None and y_val is not None:
            eval_set = [(X_val.reshape(X_val.shape[0], -1), y_val)]
            model.fit(
                X_train.reshape(X_train.shape[0], -1), y_train,
                eval_set=eval_set,
                eval_metric='rmse',
                early_stopping_rounds=10
            )
        else:
            model.fit(X_train.reshape(X_train.shape[0], -1), y_train)
        
        self.models['xgboost'] = model
        logger.info("XGBoost模型训练完成")
        return model
    
    def train_lightgbm(self, X_train, y_train, X_val=None, y_val=None):
        model = self.build_lightgbm_model()
        
        if X_val is not None and y_val is not None:
            eval_set = [(X_val.reshape(X_val.shape[0], -1), y_val)]
            model.fit(
                X_train.reshape(X_train.shape[0], -1), y_train,
                eval_set=eval_set,
                eval_metric='rmse',
                early_stopping_rounds=10
            )
        else:
            model.fit(X_train.reshape(X_train.shape[0], -1), y_train)
        
        self.models['lightgbm'] = model
        logger.info("LightGBM模型训练完成")
        return model
    
    def evaluate_model(self, model, X_test, y_test, model_type='lstm'):
        if model_type in ['lstm', 'transformer']:
            y_pred = model.predict(X_test)
        else:
            y_pred = model.predict(X_test.reshape(X_test.shape[0], -1))
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        metrics = {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
        
        logger.info(f"模型评估完成 - MSE: {mse:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")
        return metrics
    
    def save_model(self, model, model_name):
        if hasattr(model, 'save'):
            model.save(f'models/{model_name}.h5')
            model.save(f'models/{model_name}_{datetime.now().strftime("%Y%m%d")}.h5')
        else:
            model.save_model(f'models/{model_name}.txt')
        
        logger.info(f"模型已保存: models/{model_name}")
    
    def load_model(self, model_path, model_type='lstm'):
        from tensorflow.keras.models import load_model
        
        if model_type in ['lstm', 'transformer']:
            model = load_model(model_path)
        elif model_type == 'xgboost':
            model = xgb.XGBRegressor()
            model.load_model(model_path)
        elif model_type == 'lightgbm':
            model = lgb.Booster(model_file=model_path)
        
        logger.info(f"模型已加载: {model_path}")
        return model