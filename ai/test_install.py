"""
Quick test script for TrackFlow AI
Run this to verify installation
"""
import sys
from pathlib import Path

def test_imports():
    """Test if all dependencies are installed"""
    print("🧪 Testing imports...")
    
    try:
        import cv2
        print("✅ OpenCV installed")
    except ImportError:
        print("❌ OpenCV not found. Install: pip install opencv-python")
        return False
    
    try:
        import numpy
        print("✅ NumPy installed")
    except ImportError:
        print("❌ NumPy not found. Install: pip install numpy")
        return False
    
    try:
        from ultralytics import YOLO
        print("✅ Ultralytics (YOLOv8) installed")
    except ImportError:
        print("❌ Ultralytics not found. Install: pip install ultralytics")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI installed")
    except ImportError:
        print("❌ FastAPI not found. Install: pip install fastapi")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not found. Install: pip install python-dotenv")
        return False
    
    return True


def test_model_download():
    """Test model download"""
    print("\n🔽 Testing model download...")
    
    try:
        from ultralytics import YOLO
        
        print("   Downloading YOLOv8n (this may take a minute)...")
        model = YOLO('yolov8n.pt')
        print("✅ Model downloaded successfully!")
        
        # Get model info
        print(f"   Model type: {type(model)}")
        print(f"   Model file: yolov8n.pt (~6MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Model download failed: {e}")
        return False


def test_detection():
    """Test detection on dummy image"""
    print("\n🎯 Testing detection...")
    
    try:
        import numpy as np
        from ultralytics import YOLO
        
        # Create dummy image
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Load model and detect
        model = YOLO('yolov8n.pt')
        results = model.predict(dummy_image, verbose=False)
        
        print("✅ Detection works!")
        print(f"   Detected {len(results)} result(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Detection test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚗 TRACKFLOW AI - Installation Test")
    print("="*60 + "\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Some dependencies are missing!")
        print("   Run: pip install -r requirements.txt")
        return 1
    
    # Test model download
    if not test_model_download():
        print("\n❌ Model download failed!")
        return 1
    
    # Test detection
    if not test_detection():
        print("\n❌ Detection test failed!")
        return 1
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nYou can now use TrackFlow AI:")
    print("  • Detection: python main.py --source video.mp4")
    print("  • API Server: python api/main.py")
    print("\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
