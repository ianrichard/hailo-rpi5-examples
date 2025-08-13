import os
import sys
from pathlib import Path
import argparse
import yaml
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import hailo

# Add parent directory to path for hailo_apps imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from hailo_apps.hailo_app_python.core.gstreamer.gstreamer_app import app_callback_class
from hailo_apps.hailo_app_python.apps.detection_simple.detection_pipeline_simple import GStreamerDetectionApp
from hailo_apps.hailo_app_python.core.common.core import get_default_parser

# Efficient Detection with Smart Filtering
class user_app_callback_class(app_callback_class):
    def __init__(self, allowed_labels=None, min_confidence=None):
        super().__init__()
        # Efficient label filtering setup
        if allowed_labels:
            # Normalize and map synonyms
            mapped = []
            for lbl in allowed_labels:
                if lbl is None:
                    continue
                l = lbl.strip().lower()
                # Map common synonyms to COCO standard names
                if l in ("phone", "cellphone", "cell_phone"):
                    l = "cell phone"
                elif l in ("mobile", "mobile phone"):
                    l = "cell phone"
                elif l in ("face", "faces"):
                    l = "face"
                elif l in ("person", "people", "human"):
                    l = "person"
                mapped.append(l)
            self.allowed_labels = set(mapped)
            print(f"🎯 Efficient Filter: Will only show {sorted(self.allowed_labels)}")
        else:
            self.allowed_labels = None
            print("🎯 Efficient Filter: Showing all detections")
        
        self.min_confidence = min_confidence if min_confidence is not None else 0.0
        if self.min_confidence > 0:
            print(f"🎯 Efficient Filter: Minimum confidence {self.min_confidence}")
            print(f"💡 Higher confidence = fewer false positives and better performance")

    def should_keep_detection(self, label: str, confidence: float) -> bool:
        """Optimized filtering - check confidence first (faster), then label"""
        # Quick confidence check first (most efficient filter)
        if confidence < self.min_confidence:
            return False
        
        # Label whitelist check (only if labels specified)
        if self.allowed_labels and label.lower() not in self.allowed_labels:
            return False
            
        return True

# Efficient callback with optimized filtering
def app_callback(pad, info, user_data):
    user_data.increment()
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK
    
    # Get the ROI and all detections
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)
    
    frame_count = user_data.get_count()
    
    # Early exit if no filtering needed - maximum efficiency
    if not user_data.allowed_labels and user_data.min_confidence <= 0.0:
        # No filtering needed - just print count occasionally
        if frame_count % 60 == 1:  # Every 2 seconds at 30fps
            print(f"🎯 Frame {frame_count}: {len(detections)} detections (no filtering)")
        return Gst.PadProbeReturn.OK
    
    # Efficient filtering: separate into keep/remove in one pass
    detections_to_remove = []
    kept_detections = []
    
    for detection in detections:
        label = detection.get_label()
        conf = detection.get_confidence()
        
        if user_data.should_keep_detection(label, conf):
            kept_detections.append((label, conf))
        else:
            detections_to_remove.append(detection)
    
    # Only modify ROI if we need to filter (performance optimization)
    if detections_to_remove:
        try:
            # Efficient bulk removal from ROI (affects visual overlay)
            for detection in detections_to_remove:
                roi.remove_object(detection)
            
            # Reduced logging for performance
            if frame_count % 60 == 1:
                total = len(detections)
                kept = len(kept_detections)
                filtered = len(detections_to_remove)
                efficiency = (filtered / total * 100) if total > 0 else 0
                print(f"🎯 Frame {frame_count}: Kept {kept}/{total} ({efficiency:.1f}% filtered for efficiency)")
                
        except Exception as e:
            print(f"❌ ROI filtering error: {e}")
    
    # Show kept detections occasionally
    if kept_detections and frame_count % 60 == 1:
        print(f"✅ Currently showing: {[f'{l}({c:.2f})' for l, c in kept_detections[:3]]}")
    
    return Gst.PadProbeReturn.OK

def load_config(config_path):
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"✅ Loaded config from {config_path}")
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def build_parser():
    """Build argument parser with practical options"""
    parser = get_default_parser()
    
    parser.add_argument("--config", type=str, 
                       help="Path to YAML config file (overrides other settings)")
    
    parser.add_argument("--labels", nargs="*", 
                       help="Whitelist labels to show (e.g., --labels face 'cell phone' person)")
    
    parser.add_argument("--min-confidence", type=float, default=0.0, 
                       help="Minimum confidence threshold (0.0-1.0). Higher = much more efficient. Default: 0.0")
    
    parser.add_argument("--list-common-labels", action="store_true",
                       help="Show common detection labels and exit")
    
    return parser

def list_common_labels():
    """Show user what labels are commonly available"""
    print("\n🏷️  Common YOLO Detection Labels:")
    print("   Objects: person, car, truck, bus, bicycle, motorcycle")
    print("   Electronics: cell phone, laptop, tv, mouse, keyboard")
    print("   Animals: dog, cat, bird, horse, cow, sheep")
    print("   Food: banana, apple, sandwich, pizza, cake")
    print("   Sports: frisbee, sports ball, tennis racket")
    print("   Furniture: chair, couch, bed, dining table")
    print("\n💡 Efficiency Tips:")
    print("   # High efficiency - specific objects with high confidence:")
    print("   python detection_efficient.py --labels 'cell phone' --min-confidence 0.7")
    print("\n   # Medium efficiency - multiple objects with confidence filter:")
    print("   python detection_efficient.py --labels person car --min-confidence 0.5")
    print("\n   # Face detection with high confidence:")
    print("   python detection_efficient.py --labels face --min-confidence 0.8")
    print("\n🚀 Performance Notes:")
    print("   • Higher --min-confidence = fewer detections to process = better performance")
    print("   • Fewer --labels = more filtering = better performance")
    print("   • This approach combines confidence + label filtering for optimal efficiency")

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    
    if args.list_common_labels:
        list_common_labels()
        exit(0)
    
    # Load config file if specified
    config = None
    if args.config:
        config = load_config(args.config)
        if not config:
            exit(1)
    
    # Determine settings (config overrides CLI args)
    if config:
        detection_config = config.get('detection', {})
        camera_config = detection_config.get('camera', {})
        
        # Override args with config values
        camera_input = camera_config.get('input', 'usb')
        # Map "usb" alias to actual USB camera device
        if camera_input == "usb":
            camera_input = "/dev/video8"  # USB camera detected
        args.input = camera_input
        
        args.width = camera_config.get('width', 640)
        args.height = camera_config.get('height', 480)
        args.framerate = camera_config.get('fps', 30)
        
        # Detection settings
        labels = detection_config.get('labels', [])
        if labels:  # Only override if config has labels
            args.labels = labels
        args.min_confidence = detection_config.get('confidence', args.min_confidence)
        
        print(f"📋 Using config: input={args.input}, labels={args.labels}, confidence={args.min_confidence}")
    
    # Setup environment
    project_root = Path(__file__).resolve().parent.parent  # Go up to hailo-rpi5-examples root
    env_file = project_root / ".env"
    env_path_str = str(env_file)
    os.environ["HAILO_ENV_FILE"] = env_path_str
    
    # Create user data with efficient filtering
    user_data = user_app_callback_class(
        allowed_labels=args.labels, 
        min_confidence=args.min_confidence
    )
    
    print(f"\n🚀 Starting Efficient Detection:")
    print(f"   • Input: {args.input}")
    print(f"   • Confidence threshold: {args.min_confidence} (higher = more efficient)")
    print(f"   • Label filtering: {'Yes' if args.labels else 'No'}")
    if args.labels:
        print(f"   • Showing only: {args.labels}")
    print(f"   • This filters both terminal output AND video overlay efficiently!\n")

    # Update parser defaults to ensure the app uses our config values
    parser.set_defaults(input=args.input)
    parser.set_defaults(framerate=args.framerate)
    
    # Re-parse to ensure updated values are used
    args = parser.parse_args()

    # Use standard detection app - simpler and more reliable
    app = GStreamerDetectionApp(app_callback, user_data, parser)
    app.run()