# Ian's Hailo Detection Experiments

Quick custom detection setup with class filtering. Separated from main project to avoid conflicts.

## What We Did
- **Problem**: Default detection shows everything (laptops, phones, etc.) but we only want specific objects
- **Solution**: Custom filtering that removes unwanted detections from both terminal output AND video overlay
- **Environment**: Replaced conda with clean `.venv` setup (saved 3.1GB space)

## Quick Setup

```bash
# From project root
source setup_env.sh

# Go to experiments
cd ian_experiments

# Test it works
python detection.py --list-common-labels
```

## Basic Usage

```bash
# Show only people with high confidence
python detection.py --input /dev/video8 --labels person --min-confidence 0.7

# Multiple objects
python detection.py --input /dev/video8 --labels person "cell phone" laptop --min-confidence 0.5

# See available object types
python detection.py --list-common-labels
```

## Key Points
- **Filters video overlay** - unwanted objects don't appear in video window
- **Confidence filtering** - higher values = fewer false positives
- **Performance metrics** - shows "X% filtered for efficiency" 
- **Environment**: Uses `.venv` with `hailo-apps` from git (not conda)

## Environment Notes
If setup breaks, the key dependency is:
```bash
pip install git+https://github.com/hailo-ai/hailo-apps-infra.git@dev
```

Main project `setup_env.sh` was updated to use `.venv` instead of `venv_hailo_rpi_examples`.
