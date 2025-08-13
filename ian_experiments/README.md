# Ian's Detection Experiments

Custom Hailo detection with efficient class filtering and config-driven setup.

## Quick Start (Single Command!)

```bash
cd hailo-rpi5-examples/ian_experiments
./run.sh
```

That's it! The script will:
- Check if virtual environment is active (activate if needed)
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

## Features

- **One command**: Just `./run.sh` - handles everything
- **Efficient filtering**: Only shows whitelisted classes in terminal AND video
- **Config-driven**: Single YAML file controls everything  
- **USB camera support**: Automatic USB camera detection
