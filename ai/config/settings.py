"""
Configuration management for TrackFlow AI
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"
CONFIG_DIR = BASE_DIR / "config"

# Create directories if not exist
MODELS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# Model settings
MODEL_NAME = os.getenv("MODEL_NAME", "yolov8n.pt")
MODEL_PATH = MODELS_DIR / MODEL_NAME
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.35"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.5"))

# COCO class names
COCO_CLASSES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane",
    5: "bus", 6: "train", 7: "truck", 8: "boat", 9: "traffic light",
    10: "fire hydrant", 11: "stop sign", 12: "parking meter", 13: "bench",
    14: "bird", 15: "cat", 16: "dog", 17: "horse", 18: "sheep", 19: "cow",
    20: "elephant", 21: "bear", 22: "zebra", 23: "giraffe", 24: "backpack",
    25: "umbrella", 26: "handbag", 27: "tie", 28: "suitcase", 29: "frisbee",
    30: "skis", 31: "snowboard", 32: "sports ball", 33: "kite", 34: "baseball bat",
    35: "baseball glove", 36: "skateboard", 37: "surfboard", 38: "tennis racket",
    39: "bottle", 40: "wine glass", 41: "cup", 42: "fork", 43: "knife",
    44: "spoon", 45: "bowl", 46: "banana", 47: "apple", 48: "sandwich",
    49: "orange", 50: "broccoli", 51: "carrot", 52: "hot dog", 53: "pizza",
    54: "donut", 55: "cake", 56: "chair", 57: "couch", 58: "potted plant",
    59: "bed", 60: "dining table", 61: "toilet", 62: "tv", 63: "laptop",
    64: "mouse", 65: "remote", 66: "keyboard", 67: "cell phone", 68: "microwave",
    69: "oven", 70: "toaster", 71: "sink", 72: "refrigerator", 73: "book",
    74: "clock", 75: "vase", 76: "scissors", 77: "teddy bear", 78: "hair drier",
    79: "toothbrush"
}

# Vehicle classes (COCO indices)
VEHICLE_CLASSES_STR = os.getenv("VEHICLE_CLASSES", "2,3,5,7")
VEHICLE_CLASSES: List[int] = [int(x.strip()) for x in VEHICLE_CLASSES_STR.split(",")]

# Vehicle class mapping for display
VEHICLE_NAMES = {
    2: "Mobil",
    3: "Motor", 
    5: "Bus",
    7: "Truk"
}

# Processing settings (raise limit to 2GB by default)
MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "2000"))
SUPPORTED_FORMATS = os.getenv("SUPPORTED_FORMATS", "mp4,avi,mov,mkv").split(",")
FRAME_SKIP = int(os.getenv("FRAME_SKIP", "1"))
SAVE_FRAMES = os.getenv("SAVE_FRAMES", "false").lower() == "true"

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Colors for bounding boxes (BGR format for OpenCV)
COLORS = {
    2: (0, 255, 0),      # Mobil - Green
    3: (255, 0, 0),      # Motor - Blue
    5: (0, 165, 255),    # Bus - Orange
    7: (0, 0, 255),      # Truk - Red
}

def get_vehicle_name(class_id: int) -> str:
    """Get Indonesian vehicle name from class ID"""
    return VEHICLE_NAMES.get(class_id, COCO_CLASSES.get(class_id, "Unknown"))

def is_vehicle(class_id: int) -> bool:
    """Check if class ID is a vehicle"""
    return class_id in VEHICLE_CLASSES
