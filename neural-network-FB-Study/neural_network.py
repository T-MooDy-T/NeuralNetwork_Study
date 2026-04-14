"""神经网络类 - 实现三层神经网络的前向传播和反向传播"""

import numpy as np
from utils import sigmoid, sigmoid_prime, mse_loss


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        """
        初始化神经网络参数
        
        参数:
            input_size: 输入层神经元数量
            hidden_size: 隐藏层神经元数量
            output_size: 输出层神经元数量
        
        网络结构:
            输入层(input_size) → 隐藏层(hidden_size) → 输出层(output_size)
        
        参数初始化说明:
            - W1: 输入层到隐藏层的权重矩阵，shape=(input_size, hidden_size)
            - b1: 隐藏层的偏置向量，shape=(1, hidden_size)
            - W2: 隐藏层到输出层的权重矩阵，shape=(hidden_size, output_size)
            - b2: 输出层的偏置向量，shape=(1, output_size)
        
        初始化策略:
            - 权重使用 Xavier 初始化: W ~ N(0, sqrt(1/n))，n 是前一层神经元数量
              这样可以保持每层的激活值方差稳定，避免梯度消失/爆炸
            - 偏置初始化为 0
        """
        # 初始化权重（使用 Xavier 初始化，防止梯度消失）
        # Xavier 初始化: W ~ N(0, sqrt(1/n))，其中 n 是前一层神经元数量
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(1 / input_size)
        self.b1 = np.zeros((1, hidden_size))  # ⚠️ 修复：需要使用元组作为 shape 参数
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(1 / hidden_size)
        self.b2 = np.zeros((1, output_size))  # ⚠️ 修复：需要使用元组作为 shape 参数
    
    def forward(self, X):
        """
        前向传播 - 计算网络的输出
        
        参数:
            X: 输入数据，shape=(m, input_size)
               m 为样本数量
        
        返回:
            A2: 输出层激活值，shape=(m, output_size)
            cache: 存储中间结果用于反向传播
        
        计算流程:
            1. 隐藏层加权输入: Z1 = X · W1 + b1
            2. 隐藏层激活输出: A1 = sigmoid(Z1)
            3. 输出层加权输入: Z2 = A1 · W2 + b2
            4. 输出层激活输出: A2 = sigmoid(Z2)
        
        缓存中间结果的原因:
            反向传播时需要用到 Z1, A1, Z2, A2 来计算梯度
        """
        # 隐藏层计算
        Z1 = np.dot(X, self.W1) + self.b1  # 加权输入
        A1 = sigmoid(Z1)                    # 激活输出
        
        # 输出层计算
        Z2 = np.dot(A1, self.W2) + self.b2  # 加权输入
        A2 = sigmoid(Z2)                    # 激活输出
        
        # 缓存中间结果（用于反向传播）
        cache = {
            'Z1': Z1,  # 隐藏层加权输入
            'A1': A1,  # 隐藏层激活输出
            'Z2': Z2,  # 输出层加权输入
            'A2': A2   # 输出层激活输出
        }

        return A2, cache
    
    def backward(self, X, Y, cache, learning_rate=0.01):
        """
        反向传播 - 使用链式法则计算梯度并更新参数
        
        参数:
            X: 输入数据，shape=(m, input_size)
            Y: 真实标签，shape=(m, output_size)
            cache: 前向传播的中间结果
            learning_rate: 学习率（控制参数更新步长）
        
        返回:
            gradients: 包含各参数梯度的字典
        
        反向传播流程（链式法则）:
            1. 计算输出层误差: dZ2 = A2 - Y
            2. 计算输出层权重梯度: dW2 = (1/m) · A1^T · dZ2
            3. 计算输出层偏置梯度: db2 = (1/m) · sum(dZ2)
            4. 计算隐藏层误差: dZ1 = dZ2 · W2^T · sigmoid'(A1)
            5. 计算隐藏层权重梯度: dW1 = (1/m) · X^T · dZ1
            6. 计算隐藏层偏置梯度: db1 = (1/m) · sum(dZ1)
        
        参数更新（梯度下降）:
            W = W - learning_rate · dW
            b = b - learning_rate · db
        """
        m = X.shape[0]  # 样本数量
        A1 = cache['A1']
        A2 = cache['A2']
        
        # ========== 输出层梯度计算 ==========
        # 输出层误差（MSE 损失对 Z2 的导数）
        dZ2 = A2 - Y  # shape=(m, output_size)
        
        # 输出层权重梯度
        dW2 = np.dot(A1.T, dZ2) / m  # shape=(hidden_size, output_size)
        
        # 输出层偏置梯度（对所有样本求和后取平均）
        db2 = np.sum(dZ2, axis=0, keepdims=True) / m  # shape=(1, output_size)
        
        # ========== 隐藏层梯度计算 ==========
        # 隐藏层误差（链式法则：dZ1 = dZ2 · W2^T · sigmoid'(A1)）
        dZ1 = np.dot(dZ2, self.W2.T) * sigmoid_prime(A1)  # shape=(m, hidden_size)
        
        # 隐藏层权重梯度
        dW1 = np.dot(X.T, dZ1) / m  # shape=(input_size, hidden_size)
        
        # 隐藏层偏置梯度
        db1 = np.sum(dZ1, axis=0, keepdims=True) / m  # shape=(1, hidden_size)
        
        # ========== 参数更新（梯度下降）==========
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        
        # 返回梯度信息（可选，用于调试或分析）
        return {
            'dW1': dW1,
            'db1': db1,
            'dW2': dW2,
            'db2': db2
        }
        
    def train(self, X, Y, epochs=100, learning_rate=0.01):
        """
        训练神经网络
        
        参数:
            X: 输入数据，shape=(m, input_size)
            Y: 真实标签，shape=(m, output_size)
            epochs: 迭代次数（完整遍历数据集的次数）
            learning_rate: 学习率
        
        返回:
            loss: 最终的损失值
        
        训练流程:
            for epoch in 1..epochs:
                1. 前向传播：计算预测值和缓存
                2. 计算损失
                3. 反向传播：计算梯度并更新参数
                4. 打印训练进度
        
        超参数说明:
            - epochs: 训练轮数，太小可能欠拟合，太大可能过拟合
            - learning_rate: 学习率，太小收敛慢，太大可能震荡不收敛
        """
        for epoch in range(epochs):
            # 前向传播：计算预测值
            A2, cache = self.forward(X)
            
            # 计算损失（监控训练进度）
            loss = mse_loss(Y, A2)
            
            # 反向传播：计算梯度并更新参数
            self.backward(X, Y, cache, learning_rate)
            
            # 每轮打印损失（监控训练过程）
            print(f"Epoch {epoch+1}/{epochs}, Loss: {loss:.4f}")
        
        return loss