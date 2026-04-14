"""测试数据模块 - 生成神经网络训练和测试所需的数据"""

import numpy as np


def generate_xor_data():
    """
    生成 XOR 问题的测试数据
    
    XOR（异或）是一个经典的非线性分类问题：
    当两个输入相同时输出 0，不同时输出 1
    
    XOR 真值表:
    X1 | X2 | Y
    0  | 0  | 0
    0  | 1  | 1
    1  | 0  | 1
    1  | 1  | 0
    
    返回:
        X: 输入特征矩阵，shape=(4, 2)
        Y: 标签矩阵，shape=(4, 1)
    
    为什么选择 XOR:
        - XOR 问题无法用线性模型（如逻辑回归）解决
        - 需要至少一个隐藏层的神经网络才能学习
        - 是验证神经网络非线性表达能力的经典案例
    """
    X = np.array([
        [0, 0],  # 输入1
        [0, 1],  # 输入2
        [1, 0],  # 输入3
        [1, 1],  # 输入4
    ])
    
    Y = np.array([
        [0],  # 0 XOR 0 = 0
        [1],  # 0 XOR 1 = 1
        [1],  # 1 XOR 0 = 1
        [0],  # 1 XOR 1 = 0
    ])
    
    return X, Y


def generate_random_data(samples=100):
    """
    生成随机二分类数据
    
    参数:
        samples: 样本数量，默认 100
    
    返回:
        X: 输入特征矩阵，shape=(samples, 2)
        Y: 标签矩阵，shape=(samples, 1)
    
    数据生成规则:
        - X 的每个特征服从标准正态分布 N(0, 1)
        - Y = 1 当 X[:, 0] + X[:, 1] > 0，否则 Y = 0
        - 这是一个线性可分问题，可以用简单模型解决
    
    用途:
        - 测试神经网络对简单线性问题的学习能力
        - 与 XOR 的非线性问题形成对比
    """
    np.random.seed(42)  # 设置随机种子，保证结果可复现
    
    # 生成随机特征（2 个特征）
    X = np.random.randn(samples, 2)
    
    # 根据线性条件生成标签
    # X[:, 0] + X[:, 1] > 0 时为正类（1），否则为负类（0）
    Y = (X[:, 0] + X[:, 1] > 0).astype(float).reshape(-1, 1)
    
    return X, Y


# 兼容旧函数名（如果之前使用了 generate_test_data）
generate_test_data = generate_xor_data