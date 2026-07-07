@echo off

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

:: Start FastAPI Backend
echo Starting Open-ChatBot Backend...
python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000
