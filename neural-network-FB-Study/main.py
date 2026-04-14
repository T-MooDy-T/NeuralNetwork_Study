"""主程序入口 - 训练神经网络并测试 XOR 问题"""

# 导入自定义模块
from neural_network import NeuralNetwork  # 导入神经网络类
from test_data import generate_xor_data, generate_random_data  # 导入数据生成函数


def main():
    """
    主函数：训练神经网络解决 XOR 问题
    
    执行流程:
        1. 生成 XOR 训练数据
        2. 创建神经网络实例
        3. 训练神经网络
        4. 测试并打印预测结果
    """
    # ========== 1. 生成训练数据 ==========
    # XOR 数据是一个经典的非线性分类问题
    X, Y = generate_xor_data()
    print("XOR 训练数据:")
    print(f"输入 X:\n{X}")
    print(f"标签 Y:\n{Y}")
    
    # ========== 2. 创建神经网络 ==========
    # 网络结构: 输入层(2) → 隐藏层(3) → 输出层(1)
    # 输入层: 2 个神经元（对应 XOR 的两个输入）
    # 隐藏层: 3 个神经元（足够解决 XOR 问题的最小规模）
    # 输出层: 1 个神经元（二分类输出）
    nn = NeuralNetwork(input_size=2, hidden_size=3, output_size=1)
    
    # ========== 3. 训练神经网络 ==========
    print("\n开始训练神经网络...")
    # epochs=5000: 训练轮数，足够让损失收敛
    # learning_rate=1.0: 学习率，对于这个简单问题可以设置较大值
    final_loss = nn.train(X, Y, epochs=5000, learning_rate=1.0)
    
    # ========== 4. 测试预测 ==========
    print("\n训练完成！")
    print(f"最终损失: {final_loss:.4f}")
    
    # 使用训练好的网络进行预测
    predictions, _ = nn.forward(X)
    
    # 打印预测结果
    print("\n预测结果:")
    for i in range(len(X)):
        # 预测值接近 0 或 1，四舍五入后可作为分类结果
        predicted_class = round(predictions[i][0])
        print(f"输入：X={X[i]}，真实值：Y={Y[i][0]}，预测值：{predictions[i][0]:.4f}（分类：{predicted_class}）")


# 如果直接运行此文件，则执行 main 函数
if __name__ == "__main__":
    main()