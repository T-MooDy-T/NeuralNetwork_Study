CREATE DATABASE IF NOT EXISTS stock_prediction 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE stock_prediction;

CREATE TABLE IF NOT EXISTS stocks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    market VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_daily_data_stock_date ON daily_data(stock_id, date);
CREATE INDEX idx_financial_data_stock_date ON financial_data(stock_id, report_date);
CREATE INDEX idx_news_stock_time ON news(stock_id, publish_time);
CREATE INDEX idx_predictions_stock_date ON predictions(stock_id, prediction_date);

INSERT INTO stocks (code, name, industry, market) VALUES 
('600519', '贵州茅台', '白酒', 'sh'),
('000858', '五粮液', '白酒', 'sz'),
('000651', '格力电器', '家电', 'sz'),
('601318', '中国平安', '保险', 'sh'),
('000001', '平安银行', '银行', 'sz')
ON DUPLICATE KEY UPDATE name=VALUES(name), industry=VALUES(industry), market=VALUES(market);