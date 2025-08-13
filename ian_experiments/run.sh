#!/bin/bash

# Quick run script for detection experiments  
# Usage: ./run.sh (from anywhere)

# Get the directory of this script and go to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if we're in venv, if not activate it
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "🔧 Activating virtual environment..."
    source setup_env.sh
else
    echo "✅ Virtual environment already active"
fi

# Go back to ian_experiments and run detection
cd ian_experiments

echo "🚀 Starting detection..."
# Run detection with config
python detection.py --config config.yaml
