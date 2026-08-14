@echo off
title Start RuckCoin
echo Starting RuckCoin on this computer.
echo 1) The node (if Ubuntu WSL is installed)
echo 2) This wallet window
echo Leave this window open.
echo.
if exist "%~dp0..\contrib\start-all.ps1" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\contrib\start-all.ps1"
) else (
  start "" http://127.0.0.1:8870/
  python "%~dp0ruck-wallet.py"
)
if errorlevel 1 pause
