#!/bin/bash

# Start backend API
echo "Starting WhisperAI Backend..."

uvicorn api_server:app --host 0.0.0.0 --port 8000 &

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 10

# Start frontend
echo "Starting WhisperAI Frontend..."
cd /app/frontend
npm start &

# Wait for both services
echo "WhisperAI is starting up..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"

# Keep container running
wait