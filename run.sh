#!/bin/bash

# Load Intel oneAPI environment
if [ -f "/opt/intel/oneapi/setvars.sh" ]; then
    source /opt/intel/oneapi/setvars.sh
fi

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH and LD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH:.
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/llama_bin:/opt/intel/oneapi/2025.3/lib

# Build frontend static assets before launching the backend
echo "Building frontend..."
(cd src/frontend && pnpm build)

# Cleanup background processes on exit
trap "kill 0" EXIT

# Start Llama Consolidated Inference + Embedding Server (Port 8080)
echo "Starting Llama Consolidated Server..."
./llama_bin/llama-server -m models/Qwen3-4B-Hivemind-Inst-Hrtic-Ablit-Uncensored-Q4_K_M-imat.gguf --port 8080 --cache-type-k q4_0 --cache-type-v q4_0 --parallel 1 --embedding --pooling mean --cache-ram 2048 --kv-unified -ngl 99 -c 4096 --flash-attn auto &

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

# Wait for consolidated server
wait_for_server 8080 "Consolidated Server"

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
    DEBUG_LATENCY=True python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000 --log-level debug
else
    python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000
fi
