@echo off
setlocal EnableDelayedExpansion

:: Load Intel oneAPI environment
if exist "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" (
    call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
)

:: Activate virtual environment
call venv\Scripts\activate

:: Set PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%

:: Build frontend static assets before launching the backend
echo Building frontend...
pushd src\frontend
call pnpm build
popd

:: Determine bind host. Default: LAN-reachable (0.0.0.0) so phones/tablets
:: on the same Wi-Fi can connect. Run "run.bat local" to bind localhost only.
set "HOST=0.0.0.0"
if /I "%~1"=="local" set "HOST=127.0.0.1"

if "!HOST!"=="0.0.0.0" (
    :: Pick the IP on the real internet-facing route (skips Radmin/VPN/virtual adapters).
    for /f "delims=" %%i in ('powershell -NoProfile -Command "$i=(Find-NetRoute -RemoteIPAddress 8.8.8.8 -ErrorAction SilentlyContinue ^| Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254*' } ^| Select-Object -First 1 -ExpandProperty IPAddress); if(-not $i){ $i=(Get-NetIPConfiguration ^| Where-Object { $_.IPv4DefaultGateway } ^| Select-Object -First 1 -ExpandProperty IPv4Address).IPAddress }; $i"') do set "LAN_IP=%%i"
    echo.
    echo ============================================================
    echo  LAN mode ON. On your phone ^(same Wi-Fi^) open:
    echo      http://!LAN_IP!:8000
    echo.
    echo  - First launch: allow Python through Windows Firewall
    echo    when prompted ^(tick "Private networks"^).
    echo  - The app has NO login: anyone on this network can use it.
    echo    Only enable LAN mode on networks you trust.
    echo ============================================================
    echo.
)

:: Start FastAPI Backend
echo Starting Open-ChatBot Backend...
python -m uvicorn src.backend.main:app --host !HOST! --port 8000

endlocal
