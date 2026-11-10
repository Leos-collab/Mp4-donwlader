@echo off
title Baixador de Videos MP4
cd /d "%~dp0"
python app.py
if errorlevel 1 (
    echo.
    echo Ocorreu um erro ao abrir a aplicacao.
    pause
)

