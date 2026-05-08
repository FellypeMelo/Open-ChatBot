#!/bin/bash

# Load Intel oneAPI environment
if [ -f "/opt/intel/oneapi/setvars.sh" ]; then
    source /opt/intel/oneapi/setvars.sh
fi

# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH and LD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH:.
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/llama-b8984:/opt/intel/oneapi/2025.3/lib

# Build frontend static assets before launching the backend
echo "Building frontend..."
(cd frontend && pnpm build)

# Cleanup background processes on exit
trap "kill 0" EXIT

# Start Llama Inference Server (Port 8080)
echo "Starting Llama Inference Server..."
./llama-b8984/llama-server -m llama-b8984/Qwen3-4B-Hivemind-Instruct-NeoMAX-D_AU-Q6_K-imat.gguf --port 8080 --cache-type-k q8_0 --cache-type-v q8_0 -c 65536 -np 2 &

# Start Llama Embedding Server (Port 8081)
echo "Starting Llama Embedding Server..."
./llama-b8984/llama-server -m llama-b8984/Qwen3-Embedding-0.6B-Q8_0.gguf --port 8081 --embedding -c 2048 &

# Health Check Function
wait_for_server() {
    local port=$1
    local name=$2
    local retries=30
    local count=0
    
    echo "Waiting for $name to be ready on port $port..."
    while ! curl -s "http://127.0.0.1:$port/health" > /dev/null; do
        sleep 2
        count=$((count + 1))
        if [ $count -ge $retries ]; then
            echo "ERROR: $name failed to start after $((retries * 2)) seconds."
            exit 1
        fi
    done
    echo "$name is ready!"
}

# Wait for both servers
wait_for_server 8080 "Inference Server"
wait_for_server 8081 "Embedding Server"

echo "Giving model extra time to warm up..."
sleep 5

# Parse arguments
DEBUG_MODE=false
for arg in "$@"; do
    if [ "$arg" == "--debug" ]; then
        DEBUG_MODE=true
    fi
done

# Start FastAPI Backend
echo "Starting Open-ChatBot Backend..."
if [ "$DEBUG_MODE" = true ]; then
    echo "DEBUG MODE ENABLED: Full detailed logs and latency tracking active."
    DEBUG_LATENCY=True python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
else
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
