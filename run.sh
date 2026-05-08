#!/bin/bash

# Load Intel oneAPI environment
if [ -f "/opt/intel/oneapi/setvars.sh" ]; then
    source /opt/intel/oneapi/setvars.sh
fi

# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH and LD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH:.
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/llama-b8984

# Start Llama Inference Server (Port 8080)
echo "Starting Llama Inference Server..."
./llama-b8984/llama-server -m llama-b8984/L3.1-RP-Hero-InBetween-8B-D_AU-Q4_k_m.gguf --port 8080 --embedding &

# Start Llama Embedding Server (Port 8081)
echo "Starting Llama Embedding Server..."
./llama-b8984/llama-server -m llama-b8984/Qwen3-Embedding-0.6B-Q8_0.gguf --port 8081 --embedding &

# Wait for servers to start
echo "Waiting for servers to initialize..."
sleep 5

# Start FastAPI Backend
echo "Starting Open-ChatBot Backend..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Cleanup background processes on exit
trap "kill 0" EXIT
