#!/bin/bash

# Set up virtual environment and install dependencies

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Deactivate virtual environment
deactivate

echo "Setup complete! Use './run.sh' to start the application."
