@echo off
REM 校园 AI 秘书 - Windows 启动脚本

echo ========================================
echo   校园 AI 秘书 Demo
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    echo [信息] 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [警告] 未找到虚拟环境，将使用系统 Python
)

REM 检查 .env 文件
if not exist .env (
    echo [警告] 未找到 .env 文件
    echo [提示] 请复制 .env.example 为 .env 并配置 DASHSCOPE_API_KEY
    echo.
)

REM 启动服务
echo [信息] 启动校园 AI 秘书服务...
echo [信息] API 文档：http://localhost:8000/docs
echo.

python -m app.main

pause
