@echo off
REM 数据库初始化脚本

echo ========================================
echo   校园 AI 秘书 - 数据库初始化
echo ========================================
echo.

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM 运行初始化脚本
python scripts\init_db.py

echo.
pause
