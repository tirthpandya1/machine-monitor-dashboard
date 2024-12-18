#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH=.

# Start Prometheus metrics server in the background
python3 -m prometheus_client.exposition &
PROMETHEUS_PID=$!

# Start Kafka server (if needed)
# You might need to adjust this based on your Kafka setup
# kafka-server-start.sh /path/to/server.properties &
# KAFKA_PID=$!

# Run the FastAPI application with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
APP_PID=$!

# Run tests
pytest tests/

# Trap signals to clean up background processes
trap 'kill $PROMETHEUS_PID $APP_PID' SIGINT SIGTERM EXIT

# Wait for the application to finish
wait $APP_PID
