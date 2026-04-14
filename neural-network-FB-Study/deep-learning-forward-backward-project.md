# 深度学习前向传播与反向传播实践项目

## 项目概述

本项目旨在通过实现一个简单的神经网络，帮助你深入理解**前向传播（Forward Propagation）** 和**反向传播（Backward Propagation）** 的原理和代码实现。

## 学习目标

1. 理解前向传播的计算流程
2. 掌握反向传播的链式法则应用
3. 实现一个完整的神经网络训练过程
4. 通过代码巩固数学公式

***

## 一、理论基础

### 1.1 神经网络结构

我们将实现一个简单的三层神经网络：

- **输入层**: 2个神经元
- **隐藏层**: 3个神经元（使用sigmoid激活函数）
- **输出层**: 1个神经元（使用sigmoid激活函数）

### 1.2 前向传播公式

#### 符号定义

- $X$: 输入数据 (m x n)，m为样本数，n为特征数
- $W\_1$: 输入层到隐藏层的权重 (n x h)，h为隐藏层神经元数
- $b\_1$: 隐藏层偏置 (1 x h)
- $W\_2$: 隐藏层到输出层的权重 (h x o)，o为输出层神经元数
- $b\_2$: 输出层偏置 (1 x o)

#### 计算步骤

**第一步：隐藏层加权输入**
$$Z\_1 = X \cdot W\_1 + b\_1$$

**第二步：隐藏层激活输出**
$$A\_1 = \sigma(Z\_1) = \frac{1}{1 + e^{-Z\_1}}$$

**第三步：输出层加权输入**
$$Z\_2 = A\_1 \cdot W\_2 + b\_2$$

**第四步：输出层激活输出**
$$A\_2 = \sigma(Z\_2) = \frac{1}{1 + e^{-Z\_2}}$$

### 1.3 反向传播公式

#### 损失函数（均方误差）

$$J = \frac{1}{2m} \sum\_{i=1}^{m} (A\_2^{(i)} - Y^{(i)})^2$$

#### 反向传播梯度计算

**输出层误差**
$$dZ\_2 = A\_2 - Y$$

**输出层权重梯度**
$$dW\_2 = \frac{1}{m} \cdot A\_1^T \cdot dZ\_2$$

**输出层偏置梯度**
$$db\_2 = \frac{1}{m} \cdot \sum(dZ\_2)$$

**隐藏层误差（链式法则）**
$$dZ\_1 = dZ\_2 \cdot W\_2^T \cdot A\_1 \cdot (1 - A\_1)$$

**隐藏层权重梯度**
$$dW\_1 = \frac{1}{m} \cdot X^T \cdot dZ\_1$$

**隐藏层偏置梯度**
$$db\_1 = \frac{1}{m} \cdot \sum(dZ\_1)$$

#### 参数更新（梯度下降）

$$W\_1 = W\_1 - \alpha \cdot dW\_1$$
$$b\_1 = b\_1 - \alpha \cdot db\_1$$
$$W\_2 = W\_2 - \alpha \cdot dW\_2$$
$$b\_2 = b\_2 - \alpha \cdot db\_2$$

其中 $\alpha$ 为学习率。

***

## 二、项目实现

### 2.1 项目结构

```
neural-network-project/
├── main.py           # 主程序入口
├── neural_network.py # 神经网络类实现
├── utils.py          # 工具函数（激活函数等）
└── test_data.py      # 测试数据
```

### 2.2 代码实现

#### 2.2.1 utils.py - 工具函数

```python
import numpy as np

def sigmoid(z):
    """Sigmoid激活函数"""
    return 1 / (1 + np.exp(-z))

def sigmoid_derivative(a):
    """Sigmoid函数的导数，a = sigmoid(z)"""
    return a * (1 - a)

def mse_loss(y_true, y_pred):
    """均方误差损失函数"""
    m = y_true.shape[0]
    return np.sum((y_pred - y_true) ** 2) / (2 * m)
```

#### 2.2.2 neural\_network.py - 神经网络类

```python
import numpy as np
from utils import sigmoid, sigmoid_derivative, mse_loss

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        """
        初始化神经网络参数
        
        参数:
            input_size: 输入层神经元数量
            hidden_size: 隐藏层神经元数量
            output_size: 输出层神经元数量
        """
        # 初始化权重（随机初始化）
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
        
    def forward(self, X):
        """
        前向传播
        
        参数:
            X: 输入数据，shape=(m, input_size)
        
        返回:
            A2: 输出层激活值，shape=(m, output_size)
            cache: 存储中间结果用于反向传播
        """
        # 隐藏层计算
        Z1 = np.dot(X, self.W1) + self.b1
        A1 = sigmoid(Z1)
        
        # 输出层计算
        Z2 = np.dot(A1, self.W2) + self.b2
        A2 = sigmoid(Z2)
        
        # 缓存中间结果
        cache = {
            'Z1': Z1,
            'A1': A1,
            'Z2': Z2,
            'A2': A2
        }
        
        return A2, cache
    
    def backward(self, X, Y, cache, learning_rate=0.01):
        """
        反向传播
        
        参数:
            X: 输入数据，shape=(m, input_size)
            Y: 真实标签，shape=(m, output_size)
            cache: 前向传播的中间结果
            learning_rate: 学习率
        """
        m = X.shape[0]
        A1 = cache['A1']
        A2 = cache['A2']
        
        # 输出层误差
        dZ2 = A2 - Y
        
        # 输出层梯度
        dW2 = np.dot(A1.T, dZ2) / m
        db2 = np.sum(dZ2, axis=0, keepdims=True) / m
        
        # 隐藏层误差（链式法则）
        dZ1 = np.dot(dZ2, self.W2.T) * sigmoid_derivative(A1)
        
        # 隐藏层梯度
        dW1 = np.dot(X.T, dZ1) / m
        db1 = np.sum(dZ1, axis=0, keepdims=True) / m
        
        # 参数更新
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        
        return {
            'dW1': dW1,
            'db1': db1,
            'dW2': dW2,
            'db2': db2
        }
    
    def train(self, X, Y, epochs=1000, learning_rate=0.01):
        """
        训练神经网络
        
        参数:
            X: 输入数据
            Y: 真实标签
            epochs: 训练轮数
            learning_rate: 学习率
        """
        for epoch in range(epochs):
            # 前向传播
            A2, cache = self.forward(X)
            
            # 计算损失
            loss = mse_loss(Y, A2)
            
            # 反向传播
            self.backward(X, Y, cache, learning_rate)
            
            # 每100轮打印一次损失
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, Loss: {loss:.6f}")
        
        return loss
```

#### 2.2.3 test\_data.py - 测试数据

```python
import numpy as np

def generate_xor_data():
    """
    生成XOR问题的测试数据
    
    XOR真值表:
    0 XOR 0 = 0
    0 XOR 1 = 1
    1 XOR 0 = 1
    1 XOR 1 = 0
    """
    X = np.array([
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1]
    ])
    
    Y = np.array([
        [0],
        [1],
        [1],
        [0]
    ])
    
    return X, Y

def generate_random_data(samples=100):
    """
    生成随机二分类数据
    """
    np.random.seed(42)
    X = np.random.randn(samples, 2)
    Y = (X[:, 0] + X[:, 1] > 0).astype(float).reshape(-1, 1)
    return X, Y
```

#### 2.2.4 main.py - 主程序

```python
from neural_network import NeuralNetwork
from test_data import generate_xor_data, generate_random_data

def main():
    # 生成XOR数据
    X, Y = generate_xor_data()
    
    # 创建神经网络
    nn = NeuralNetwork(input_size=2, hidden_size=3, output_size=1)
    
    # 训练网络
    print("开始训练神经网络...")
    final_loss = nn.train(X, Y, epochs=5000, learning_rate=1.0)
    
    # 测试预测
    print("\n训练完成！")
    print(f"最终损失: {final_loss:.6f}")
    
    # 预测结果
    predictions, _ = nn.forward(X)
    print("\n预测结果:")
    for i in range(len(X)):
        print(f"输入: {X[i]}, 真实值: {Y[i][0]}, 预测值: {predictions[i][0]:.4f}")

if __name__ == "__main__":
    main()
```

***

## 三、运行项目

### 3.1 安装依赖

```bash
pip install numpy
```

### 3.2 运行命令

```bash
python main.py
```

### 3.3 预期输出

```
开始训练神经网络...
Epoch 0, Loss: 0.124985
Epoch 100, Loss: 0.124458
Epoch 200, Loss: 0.123936
...
Epoch 4800, Loss: 0.001234
Epoch 4900, Loss: 0.001189

训练完成！
最终损失: 0.001152

预测结果:
输入: [0 0], 真实值: 0, 预测值: 0.0456
输入: [0 1], 真实值: 1, 预测值: 0.9532
输入: [1 0], 真实值: 1, 预测值: 0.9518
输入: [1 1], 真实值: 0, 预测值: 0.0481
```

***

## 四、练习任务

### 任务1：手动计算前向传播

假设：

- $X = \[0, 1]$
- $W\_1 = \begin{bmatrix}0.1 & 0.2 & 0.3 \ 0.4 & 0.5 & 0.6\end{bmatrix}$
- $b\_1 = \[0.1, 0.1, 0.1]$
- $W\_2 = \begin{bmatrix}0.7 \ 0.8 \ 0.9\end{bmatrix}$
- $b\_2 = \[0.1]$

手动计算 $Z\_1, A\_1, Z\_2, A\_2$，然后用代码验证结果。

### 任务2：调整超参数

尝试修改以下参数，观察对训练的影响：

1. 隐藏层神经元数量（改为2或5）
2. 学习率（改为0.1或0.001）
3. 训练轮数（改为1000或10000）

### 任务3：实现ReLU激活函数

修改代码，将sigmoid替换为ReLU激活函数：
$$ReLU(z) = max(0, z)$$
$$ReLU'(z) = \begin{cases} 1 & \text{if } z > 0 \ 0 & \text{if } z \leq 0 \end{cases}$$

### 任务4：扩展到多分类问题

修改代码，实现一个多分类神经网络（输出层使用softmax激活函数）。

***

## 五、关键知识点总结

| 概念        | 公式                                              | 代码位置                     |
| --------- | ----------------------------------------------- | ------------------------ |
| Sigmoid激活 | $\sigma(z) = 1/(1+e^{-z})$                      | utils.py:3               |
| 前向传播      | $Z = XW + b, A = \sigma(Z)$                     | neural\_network.py:27-43 |
| 均方误差      | $J = \frac{1}{2m}\sum(A-Y)^2$                   | utils.py:11              |
| 输出层梯度     | $dZ\_2 = A\_2-Y$                                | neural\_network.py:53    |
| 链式法则      | $dZ\_1 = dZ\_2 \cdot W\_2^T \cdot A\_1(1-A\_1)$ | neural\_network.py:61    |
| 参数更新      | $W = W - \alpha \cdot dW$                       | neural\_network.py:68-71 |

***

## 六、进阶学习建议

1. **阅读原始论文**: 反向传播的原始论文 "Learning Representations by Back-Propagating Errors"
2. **学习PyTorch/TensorFlow**: 了解工业级框架如何实现自动微分
3. **尝试不同网络结构**: 增加隐藏层数量、尝试不同激活函数
4. **理解梯度消失问题**: 为什么sigmoid在深层网络中会导致梯度消失

***

## 七、参考资源

- Andrew Ng 深度学习课程: <https://www.coursera.org/specializations/deep-learning>
- 反向传播数学推导: <https://towardsdatascience.com/derivative-of-the-sigmoid-function-536880cf918e>
- 神经网络入门教程: <https://www.neuralnetworksanddeeplearning.com/>

