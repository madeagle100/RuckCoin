@echo off
title RuckCoin wallet
cd /d "%~dp0"
echo Starting the RuckCoin wallet...
echo Leave this window open.
echo.
start "" http://127.0.0.1:8870/
python ruck-wallet.py
if errorlevel 1 pause
