#!/bin/bash
# 校园 AI 秘书 - Linux/macOS 启动脚本

echo "========================================"
echo "  校园 AI 秘书 Demo"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

echo "[信息] Python 版本：$(python3 --version)"

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    echo "[信息] 激活虚拟环境..."
    source venv/bin/activate
else
    echo "[警告] 未找到虚拟环境，将使用系统 Python"
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "[警告] 未找到 .env 文件"
    echo "[提示] 请复制 .env.example 为 .env 并配置 DASHSCOPE_API_KEY"
    echo ""
fi

# 启动服务
echo "[信息] 启动校园 AI 秘书服务..."
echo "[信息] API 文档：http://localhost:8000/docs"
echo ""

python3 -m app.main
