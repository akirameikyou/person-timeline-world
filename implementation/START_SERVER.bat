@echo off
setlocal
cd /d "%~dp0"
set "PORT="
for /f "delims=" %%P in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=8000; while($p -le 8010){if(-not (Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue)){break}; $p++}; Write-Output $p"') do set "PORT=%%P"
if not defined PORT set "PORT=8000"

echo.
echo Person Timeline World v1.0
echo URL: http://127.0.0.1:%PORT%/
echo.
echo Opening the browser...
start "" "http://127.0.0.1:%PORT%/"
echo Close this window to stop the server.
echo.
python -m http.server %PORT% --bind 127.0.0.1
if errorlevel 1 (
  echo.
  echo Python server could not start. Please check that Python is installed.
  pause
)
endlocal
