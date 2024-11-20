@echo off
start python startscr.py
setlocal

set PYTHON_FILE=panelsetting.py

for /f "tokens=1,2 delims==" %%i in ('python read-config.py %PYTHON_FILE%') do (
    if "%%i"=="IP" set LIP=%%j
    if "%%i"=="PORT" set LPORT=%%j
)

set URL=http://%LIP%:%LPORT%
start "" %URL%
endlocal
