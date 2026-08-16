@echo off
title Start RuckCoin
echo Starting RuckCoin on this computer.
echo Leave this window open.
echo.
if exist "%~dp0..\contrib\start-all.ps1" (
  rem Full repo on the builder PC: keep the private WSL test node.
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\contrib\start-all.ps1"
) else if exist "%~dp0start-node.ps1" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-node.ps1"
) else (
  echo No node starter found. Opening the wallet only.
  echo Start a node first. See the Start page for your computer.
  start "" http://127.0.0.1:8870/
  python "%~dp0ruck-wallet.py"
)
if errorlevel 1 pause
