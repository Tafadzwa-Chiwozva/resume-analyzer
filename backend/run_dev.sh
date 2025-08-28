#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Set development environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run the Flask application
python app.py 