#!/bin/bash

# Ensure script is run from the project root
cd "$(dirname "$0")"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

# Ensure we're using Python 3.12
if [[ "$PYTHON_VERSION" != "3.12" ]]; then
    echo "Error: This project requires Python 3.12"
    exit 1
fi

# Check if concurrently is installed
if ! command -v concurrently &> /dev/null; then
    echo "Installing concurrently globally..."
    npm install -g concurrently
fi

# Install backend dependencies
echo "Setting up backend virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install setuptools first
pip install --upgrade pip setuptools wheel

# Install requirements with additional flags
pip install --use-pep517 -r requirements.txt

deactivate
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start both backend and frontend
echo "Starting Machine Monitor Application..."
npm start
