# Ian's Detection Experiments

Custom Hailo detection with efficient class filtering and config-driven setup.

## Quick Start (Single Command!)

```bash
cd ian_experiments
./run.sh
```

That's it! The script will:
- Activate the virtual environment  
- Run detection with your USB camera
- Filter to only show faces, cell phones, and people
- Display both terminal output AND video overlay

## Configuration

Edit `config.yaml` to customize:

```yaml
detection:
  camera:
    input: "usb"        # "usb" for USB camera, or full path like "/dev/video0" 
    width: 640
    height: 480
    fps: 30
  labels:
    - "face"
    - "cell phone" 
    - "person"
  confidence: 0.5       # Higher = fewer false positives, better performance
```

## Manual Usage

```bash
# From project root
source setup_env.sh
cd ian_experiments

# Run with config
python detection.py --config config.yaml

# Or with command line args
python detection.py --input /dev/video8 --labels face "cell phone" --min-confidence 0.5
```

## Features

- **Efficient filtering**: Only shows whitelisted classes in terminal AND video
- **Config-driven**: Single YAML file controls everything
- **USB camera support**: Automatic USB camera detection
- **One-command run**: Just `./run.sh` and go!
