# 股价预测项目

## 项目概述

本项目旨在通过爬取企业财报、税收、年报等多维度数据，结合历史股价走势，利用机器学习算法进行股价预测，并通过Web页面进行动态可视化展示。

## 技术栈

### 后端技术
- **语言**: Python 3.8+
- **爬虫框架**: Scrapy / BeautifulSoup4 / Requests
- **机器学习**: TensorFlow 2.x / PyTorch / scikit-learn
- **数据库**: PostgreSQL / MySQL / SQLite
- **API框架**: FastAPI
- **数据处理**: Pandas / NumPy

### 前端技术
- **框架**: Vue.js 3 / React
- **图表库**: ECharts / D3.js
- **UI组件**: Ant Design / Element Plus
- **样式**: TailwindCSS 3

### 部署
- **容器**: Docker / Docker Compose
- **调度**: Celery / APScheduler

## 项目架构

```
stock-prediction-project/
├── data/                    # 数据存储目录
│   ├── raw/                # 原始爬取数据
│   ├── processed/          # 预处理后数据
│   └── models/             # 模型文件
├── crawler/                # 爬虫模块
│   ├── __init__.py
│   ├── stock_crawler.py    # 股票数据爬虫
│   ├── finance_crawler.py  # 财务数据爬虫
│   └── news_crawler.py     # 新闻资讯爬虫
├── ml_models/              # 机器学习模块
│   ├── __init__.py
│   ├── data_processor.py   # 数据预处理
│   ├── model_trainer.py    # 模型训练
│   ├── predictor.py        # 预测模块
│   └── models/             # 模型定义
├── web/                    # Web模块
│   ├── backend/            # FastAPI后端
│   └── frontend/           # Vue/React前端
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── db_utils.py         # 数据库工具
│   └── logger.py           # 日志工具
├── tests/                  # 测试模块
├── requirements.txt        # 依赖清单
└── main.py                # 项目入口
```

## 核心功能模块

### 1. 数据爬取模块

**数据来源**:
- 股票行情数据: 东方财富网、同花顺、新浪财经
- 财务报表数据: 巨潮资讯网、企业官网投资者关系栏目
- 税务数据: 国家税务总局、上市公司公告
- 新闻资讯: 财经媒体、行业分析报告

**爬取内容**:
- 日K线数据（开盘价、收盘价、最高价、最低价、成交量）
- 财务报表（资产负债表、利润表、现金流量表）
- 财务指标（市盈率、市净率、ROE、毛利率等）
- 新闻舆情、行业动态

### 2. 数据预处理模块

**功能**:
- 数据清洗（缺失值处理、异常值检测）
- 特征工程（特征提取、归一化、标准化）
- 时间序列处理（滑动窗口、滞后特征）
- 数据集成（多源数据融合）

### 3. 机器学习模型模块

**算法选择**:
- LSTM（长短期记忆网络）- 时间序列预测首选
- Transformer - 捕捉长期依赖关系
- XGBoost/LightGBM - 特征重要性分析
- ARIMA/SARIMA - 传统时间序列模型

**模型架构**:
- 输入层: 历史股价、财务指标、舆情特征
- 隐藏层: LSTM/Transformer编码器
- 输出层: 股价预测值（回归任务）

### 4. Web可视化模块

**功能**:
- 实时股价走势图
- 预测结果展示
- 财务数据仪表盘
- 模型性能指标展示
- 交互式数据探索

## 开发步骤

### 阶段一：环境搭建（1-2天）
1. 安装Python环境
2. 配置虚拟环境
3. 安装依赖包
4. 配置数据库

### 阶段二：数据爬取模块开发（3-5天）
1. 设计爬虫架构
2. 实现股票数据爬取
3. 实现财务数据爬取
4. 实现新闻资讯爬取
5. 数据存储到数据库

### 阶段三：数据预处理（2-3天）
1. 数据清洗脚本
2. 特征工程实现
3. 数据集划分

### 阶段四：模型开发（5-7天）
1. LSTM模型实现
2. Transformer模型实现
3. 模型训练与调优
4. 模型评估

### 阶段五：Web后端开发（3-4天）
1. FastAPI服务搭建
2. API接口设计
3. 数据库接口
4. 模型预测接口

### 阶段六：Web前端开发（5-7天）
1. Vue/React项目初始化
2. 图表组件开发
3. 仪表盘页面开发
4. 交互功能实现

### 阶段七：测试与部署（2-3天）
1. 单元测试
2. 集成测试
3. Docker容器化
4. 部署上线

## API接口设计

### 股票数据接口
- `GET /api/stocks` - 获取股票列表
- `GET /api/stocks/{code}/history` - 获取历史股价
- `GET /api/stocks/{code}/financial` - 获取财务数据

### 预测接口
- `POST /api/predict` - 提交预测请求
- `GET /api/predict/{id}` - 获取预测结果

### 数据接口
- `GET /api/indicators` - 获取指标列表
- `GET /api/news` - 获取新闻资讯

## 数据库设计

### stocks表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| code | VARCHAR | 股票代码 |
| name | VARCHAR | 股票名称 |
| industry | VARCHAR | 所属行业 |
| market | VARCHAR | 市场（沪/深/港/美） |

### daily_data表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| stock_id | INT | 股票ID |
| date | DATE | 日期 |
| open | FLOAT | 开盘价 |
| close | FLOAT | 收盘价 |
| high | FLOAT | 最高价 |
| low | FLOAT | 最低价 |
| volume | BIGINT | 成交量 |

### financial_data表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| stock_id | INT | 股票ID |
| report_date | DATE | 报告日期 |
| eps | FLOAT | 每股收益 |
| pe | FLOAT | 市盈率 |
| pb | FLOAT | 市净率 |
| revenue | FLOAT | 营业收入 |
| net_profit | FLOAT | 净利润 |

## 风险提示

1. **投资风险**: 本项目仅供学习研究，不构成投资建议
2. **数据风险**: 爬取数据可能存在延迟或不准确
3. **市场风险**: 股价受多种因素影响，预测结果仅供参考

## 许可证

MIT License