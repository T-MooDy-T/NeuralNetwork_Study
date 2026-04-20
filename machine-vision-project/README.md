# 机器视觉项目

一个简洁高效的机器视觉项目，支持手写数字识别和简单图案检测。

## 项目目标

- 实现基于机器学习的手写数字识别（0-9）
- 实现简单几何图案检测（圆形、矩形、三角形）
- 提供简洁的API接口，易于集成和扩展
- 保证快速运行速度，适合实时应用场景

## 技术方案

### 1. 手写数字识别

- **数据集**: 使用MNIST数据集（手写数字图片，28x28像素）
- **模型**: 轻量级卷积神经网络（CNN）
- **框架**: PyTorch
- **准确率目标**: >98%

### 2. 简单图案检测

- **图案类型**: 圆形、矩形、三角形
- **检测方法**: 基于OpenCV的轮廓检测和形状匹配
- **特征提取**: 面积、周长、近似多边形顶点数

## 项目结构

```
machine-vision-project/
├── README.md           # 项目文档
├── requirements.txt    # 依赖列表
├── src/
│   ├── __init__.py
│   ├── digit_recognizer.py    # 手写数字识别模块
│   ├── shape_detector.py      # 图案检测模块
│   └── utils.py               # 工具函数
├── models/
│   └── digit_model.pth        # 预训练模型（运行后生成）
├── data/
│   └── samples/               # 测试样本图片
└── main.py                    # 主入口
```

## 依赖安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 手写数字识别

```python
from src.digit_recognizer import DigitRecognizer

recognizer = DigitRecognizer()
digit = recognizer.predict(image_path)
print(f"识别结果: {digit}")
```

### 2. 图案检测

```python
from src.shape_detector import ShapeDetector

detector = ShapeDetector()
shapes = detector.detect(image_path)
print(f"检测到的图案: {shapes}")
```

## 运行示例

```bash
python main.py
```

## 性能特点

- 轻量级模型，快速加载和推理
- 支持实时图片输入
- 代码简洁，易于理解和扩展