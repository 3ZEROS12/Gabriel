@echo off
chcp 65001 >nul
title 加百列
cd /d "%~dp0"
echo --------------------------------------------------
echo   🕊️ 正在启动加百列...
echo   浏览器即将自动打开控制台
echo --------------------------------------------------
.\venv\Scripts\python.exe -m src.main
