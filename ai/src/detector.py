"""
Vehicle Detector using YOLOv8 + COCO pretrained model
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from ultralytics import YOLO
from config.settings import (
    MODEL_NAME,
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    VEHICLE_CLASSES,
    get_vehicle_name,
    is_vehicle,
    MODELS_DIR
)


class VehicleDetector:
    """
    YOLOv8-based vehicle detector for TrackFlow
    Detects: Mobil, Motor, Truk, Bus
    """
    
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        conf_threshold: float = CONFIDENCE_THRESHOLD,
        iou_threshold: float = IOU_THRESHOLD
    ):
        """
        Initialize vehicle detector
        
        Args:
            model_name: YOLOv8 model name (e.g., 'yolov8n.pt')
            conf_threshold: Confidence threshold for detection
            iou_threshold: IOU threshold for NMS
        """
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.model = None
        
        print(f"🚗 Initializing TrackFlow Vehicle Detector...")
        print(f"   Model: {model_name}")
        print(f"   Confidence: {conf_threshold}")
        print(f"   IOU: {iou_threshold}")
        
        self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model (auto-download if not exists)"""
        try:
            model_path = MODELS_DIR / self.model_name
            
            if not model_path.exists():
                print(f"📥 Downloading {self.model_name}...")
                self.model = YOLO(self.model_name)
                print(f"✅ Model downloaded to {MODELS_DIR}")
            else:
                print(f"✅ Loading model from {model_path}")
                self.model = YOLO(str(model_path))
            
            print(f"✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def detect_image(
        self,
        image: np.ndarray,
        filter_vehicles: bool = True,
        imgsz: int = 640
    ) -> List[Dict[str, Any]]:
        """
        Detect vehicles in a single image
        
        Args:
            image: Input image (numpy array)
            filter_vehicles: Only return vehicle detections
            
        Returns:
            List of detections with format:
            [
                {
                    'class_id': int,
                    'class_name': str,
                    'confidence': float,
                    'bbox': [x1, y1, x2, y2]
                },
                ...
            ]
        """
        if self.model is None:
            raise RuntimeError("Model not loaded!")
        
        # Run inference with enhanced parameters for better accuracy
        results = self.model.predict(
            source=image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=VEHICLE_CLASSES if filter_vehicles else None,
            verbose=False,
            imgsz=imgsz,            # Image size for inference (lower = faster, higher = more accurate)
            half=False,             # Use FP32 for better accuracy (vs FP16)
            augment=True,           # Test-time augmentation for better detection
            agnostic_nms=False,     # Class-specific NMS
            max_det=300             # Maximum detections per image
        )
        
        # Parse results
        detections = []
        
        if len(results) > 0:
            result = results[0]
            
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy().astype(int)
                
                for box, conf, cls_id in zip(boxes, confidences, class_ids):
                    if filter_vehicles and not is_vehicle(cls_id):
                        continue
                    
                    detection = {
                        'class_id': int(cls_id),
                        'class_name': get_vehicle_name(cls_id),
                        'confidence': float(conf),
                        'bbox': [float(x) for x in box]  # [x1, y1, x2, y2]
                    }
                    detections.append(detection)
        
        return detections
    
    def detect_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        show_progress: bool = True,
        frame_skip: int = 1,
        show_preview: bool = False,
        imgsz: int = 640
    ) -> Dict[str, Any]:
        """
        Detect vehicles in video
        
        Args:
            video_path: Path to input video
            output_path: Path to save output video (optional)
            show_progress: Show progress bar
            frame_skip: Process every Nth frame (1 = all frames)
            show_preview: Show real-time preview window
            
        Returns:
            Dictionary with detection statistics and results
        """
        if self.model is None:
            raise RuntimeError("Model not loaded!")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📹 Processing video: {video_path}")
        print(f"   Resolution: {frame_width}x{frame_height}")
        print(f"   FPS: {fps}")
        print(f"   Total frames: {total_frames}")
        
        # Initialize video writer if output path is provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (frame_width, frame_height)
            )
        
        # Statistics
        frame_detections = []
        vehicle_counts = {cls_id: 0 for cls_id in VEHICLE_CLASSES}
        
        frame_idx = 0
        processed_frames = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Skip frames if needed
                if frame_idx % frame_skip != 0:
                    frame_idx += 1
                    continue
                
                # Detect vehicles in frame
                detections = self.detect_image(frame, filter_vehicles=True, imgsz=imgsz)
                
                # Count detections
                for det in detections:
                    vehicle_counts[det['class_id']] += 1
                
                frame_detections.append({
                    'frame_idx': frame_idx,
                    'timestamp': frame_idx / fps,
                    'detections': detections
                })
                
                # Draw detections on frame
                annotated_frame = self._draw_detections(frame, detections)
                
                # Write to output video
                if writer:
                    writer.write(annotated_frame)
                
                # Show preview window
                if show_preview:
                    # Resize for display if too large
                    display_frame = annotated_frame
                    if frame_width > 1280:
                        scale = 1280 / frame_width
                        new_width = 1280
                        new_height = int(frame_height * scale)
                        display_frame = cv2.resize(annotated_frame, (new_width, new_height))
                    
                    cv2.imshow('TrackFlow - Vehicle Detection (Press Q to quit)', display_frame)
                    
                    # Check for quit key
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("\n⏸️  Preview window closed by user")
                        break
                
                processed_frames += 1
                
                if show_progress and processed_frames % 30 == 0:
                    progress = (frame_idx / total_frames) * 100
                    print(f"   Progress: {progress:.1f}% ({processed_frames} frames)", end='\r')
                
                frame_idx += 1
            
        finally:
            cap.release()
            if writer:
                writer.release()
            if show_preview:
                cv2.destroyAllWindows()
        
        print(f"\n✅ Video processing complete!")
        print(f"   Processed: {processed_frames} frames")
        print(f"   Detections: {sum(vehicle_counts.values())}")
        
        # Return results
        return {
            'video_info': {
                'path': video_path,
                'fps': fps,
                'width': frame_width,
                'height': frame_height,
                'total_frames': total_frames,
                'processed_frames': processed_frames
            },
            'statistics': {
                'total_detections': sum(vehicle_counts.values()),
                'vehicle_counts': {
                    get_vehicle_name(cls_id): count 
                    for cls_id, count in vehicle_counts.items()
                },
                'average_per_frame': sum(vehicle_counts.values()) / processed_frames if processed_frames > 0 else 0
            },
            'frame_detections': frame_detections,
            'output_path': output_path
        }
    
    def _draw_detections(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on image
        
        Args:
            image: Input image
            detections: List of detections
            
        Returns:
            Annotated image
        """
        from config.settings import COLORS
        
        annotated = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            class_id = det['class_id']
            class_name = det['class_name']
            confidence = det['confidence']
            
            # Get color for this vehicle type
            color = COLORS.get(class_id, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Draw label background
            label = f"{class_name} {confidence:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(annotated, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
            
            # Draw label text
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )
        
        return annotated
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'confidence_threshold': self.conf_threshold,
            'iou_threshold': self.iou_threshold,
            'vehicle_classes': [get_vehicle_name(cls_id) for cls_id in VEHICLE_CLASSES]
        }
