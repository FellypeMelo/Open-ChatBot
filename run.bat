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

:: Start Llama Consolidated Inference + Embedding Server (Port 8080)
echo Starting Llama Consolidated Server...
start /B llama_bin\llama-server.exe -m models\Qwen3-4B-Hivemind-Inst-Hrtic-Ablit-Uncensored-Q4_K_M-imat.gguf --port 8080 --cache-type-k q4_0 --cache-type-v q4_0 --parallel 1 --embedding --pooling mean --cache-ram 2048 --kv-unified -ngl 99 -c 4096 --flash-attn auto

:: Wait for servers to start
echo Waiting for servers to initialize...
ping -n 6 127.0.0.1 >nul

:: Start FastAPI Backend
echo Starting Open-ChatBot Backend...
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000
