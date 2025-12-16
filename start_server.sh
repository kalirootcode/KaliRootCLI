#!/bin/bash
echo "🚀 Starting KaliRoot CLI API Server (Local)..."
source .env
export KRCLI_API_URL=http://localhost:8000
./venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
