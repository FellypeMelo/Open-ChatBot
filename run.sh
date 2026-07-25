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
./llama_bin/llama-server -m models/YOUR-MODEL-HERE.gguf --port 8080 --cache-type-k q8_0 --cache-type-v turbo3 --parallel 1 --embedding --pooling mean --cache-ram 2048 --kv-unified -ngl 99 -c 49152 --flash-attn auto &

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

# Parse arguments. Default host is LAN-reachable (0.0.0.0) so phones/tablets
# on the same Wi-Fi can connect. Pass "local" to bind localhost only.
DEBUG_MODE=false
HOST="0.0.0.0"
for arg in "$@"; do
    if [ "$arg" == "--debug" ]; then
        DEBUG_MODE=true
    fi
    if [ "$arg" == "local" ] || [ "$arg" == "--local" ]; then
        HOST="127.0.0.1"
    fi
done

# LAN mode: expose to local network and print the phone-reachable URL.
if [ "$HOST" == "0.0.0.0" ]; then
    LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
    [ -z "$LAN_IP" ] && LAN_IP=$(ipconfig getifaddr en0 2>/dev/null)
    echo "============================================================"
    echo " LAN mode ON. On your phone (same Wi-Fi) open:"
    echo "     http://${LAN_IP}:8000"
    echo " The app has NO login: anyone on this network can use it."
    echo " Only enable LAN mode on networks you trust."
    echo "============================================================"
fi

# Start FastAPI Backend
echo "Starting Open-ChatBot Backend..."
if [ "$DEBUG_MODE" = true ]; then
    echo "DEBUG MODE ENABLED: Full detailed logs and latency tracking active."
    DEBUG_LATENCY=True python -m uvicorn src.backend.main:app --host "$HOST" --port 8000 --log-level debug
else
    python -m uvicorn src.backend.main:app --host "$HOST" --port 8000
fi
