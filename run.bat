@echo off

:: Load Intel oneAPI environment
if exist "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" (
    call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
)

:: Activate virtual environment
call .venv\Scripts\activate

:: Set PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%

:: Build frontend static assets before launching the backend
echo Building frontend...
pushd frontend
pnpm build
popd

:: Start Llama Inference Server (Port 8080)
echo Starting Llama Inference Server...
start /B llama-b8984\llama-server.exe -m llama-b8984\Qwen3-4B-Hivemind-Instruct-NeoMAX-D_AU-Q6_K-imat.gguf --port 8080 --cache-type-k q8_0 --cache-type-v q8_0

:: Start Llama Embedding Server (Port 8081)
echo Starting Llama Embedding Server...
start /B llama-b8984\llama-server.exe -m llama-b8984\Qwen3-Embedding-0.6B-Q8_0.gguf --port 8081 --embedding

:: Wait for servers to start
echo Waiting for servers to initialize...
timeout /t 5 /nobreak

:: Start FastAPI Backend
echo Starting Open-ChatBot Backend...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
