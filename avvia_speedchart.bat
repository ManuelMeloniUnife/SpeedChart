@echo off
echo Avvio SpeedChart...
cd /d %~dp0
call venv\Scripts\activate.bat
python run_speedchart.py