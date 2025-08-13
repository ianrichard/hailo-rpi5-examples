#!/bin/bash

# Quick run script for detection experiments
# Usage: ./run.sh

# Get the directory of this script and go to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Activate environment from project root
source setup_env.sh

# Go back to ian_experiments and run detection
cd ian_experiments

# Run detection with config
python detection.py --config config.yaml
