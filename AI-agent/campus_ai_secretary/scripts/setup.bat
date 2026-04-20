@echo off
REM 校园 AI 秘书 - Windows 安装脚本

echo ========================================
echo   校园 AI 秘书 - 安装向导
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo [步骤 1/4] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)

echo [步骤 2/4] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [步骤 3/4] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

echo [步骤 4/4] 配置环境变量...
if not exist .env (
    copy .env.example .env
    echo [提示] 请编辑 .env 文件配置 DASHSCOPE_API_KEY
) else (
    echo [信息] .env 文件已存在
)

echo.
echo ========================================
echo   安装完成!
echo ========================================
echo.
echo 下一步:
echo 1. 编辑 .env 文件，配置 DASHSCOPE_API_KEY
echo 2. 确保 MySQL 服务已启动
echo 3. 运行：scripts\init_db.bat  初始化数据库
echo 4. 运行：scripts\run_demo.bat  启动服务
echo 5. 访问：http://localhost:8000/admin
echo.

pause
