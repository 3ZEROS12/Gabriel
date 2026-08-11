@echo off
chcp 65001 >nul
title 启动 Gabriel 副屏
cd /d "%~dp0"
echo --------------------------------------------------
echo   👼 正在启动 Gabriel 副屏控制台...
echo   浏览器将自动打开，请稍候...
echo --------------------------------------------------
.\venv\Scripts\python.exe -m src.main
