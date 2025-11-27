"""
Vehicle Tracker using YOLOv8 built-in tracking (ByteTrack)
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from collections import defaultdict
from ultralytics import YOLO
from config.settings import (
    MODEL_NAME,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    VEHICLE_CLASSES,
    get_vehicle_name,
    COLORS,
    MODELS_DIR
)


class VehicleTracker:
    """
    Vehicle tracker with unique IDs for each vehicle
    Uses YOLOv8's built-in ByteTrack algorithm
    """
    
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        conf_threshold: float = CONFIDENCE_THRESHOLD,
        iou_threshold: float = IOU_THRESHOLD,
        tracker_config: str = "bytetrack.yaml"
    ):
        """
        Initialize vehicle tracker
        
        Args:
            model_name: YOLOv8 model name
            conf_threshold: Confidence threshold
            iou_threshold: IOU threshold
            tracker_config: Tracker configuration file
        """
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.tracker_config = tracker_config
        self.model = None
        
        # Tracking statistics
        self.track_history = defaultdict(list)  # Track ID -> list of centers
        self.track_classes = {}  # Track ID -> class ID
        self.unique_vehicles = set()  # Set of unique track IDs
        self.crossed_vehicles = set()  # Track IDs that crossed the line
        self.counting_line = None  # ((x1,y1), (x2,y2))
        
        print(f"🎯 Initializing TrackFlow Vehicle Tracker...")
        print(f"   Model: {model_name}")
        print(f"   Tracker: {tracker_config}")
        
        self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            model_path = MODELS_DIR / self.model_name
            
            if not model_path.exists():
                print(f"📥 Downloading {self.model_name}...")
                self.model = YOLO(self.model_name)
            else:
                self.model = YOLO(str(model_path))
            
            print(f"✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def _check_line_crossing(self, point1, point2, line_start, line_end):
        """
        Check if a line segment (point1 -> point2) crosses the counting line
        Uses line intersection algorithm
        
        Args:
            point1: (x, y) start point of vehicle movement
            point2: (x, y) end point of vehicle movement
            line_start: (x, y) start of counting line
            line_end: (x, y) end of counting line
            
        Returns:
            True if lines intersect, False otherwise
        """
        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = line_start
        x4, y4 = line_end
        
        # Calculate denominators
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if abs(denom) < 1e-10:
            return False  # Lines are parallel
        
        # Calculate intersection point parameters
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        # Check if intersection is within both line segments
        if 0 <= t <= 1 and 0 <= u <= 1:
            return True
        
        return False
    
    def track_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        counting_line: Optional[tuple] = None,
        show_progress: bool = True,
        draw_trails: bool = True,
        max_trail_length: int = 30,
        show_preview: bool = False,
        imgsz: int = 640
    ) -> Dict[str, Any]:
        """
        Track vehicles in video with unique IDs and optional line crossing count
        
        Args:
            video_path: Path to input video
            output_path: Path to save output video
            counting_line: Optional tuple ((x1,y1), (x2,y2)) for line crossing detection
            show_progress: Show progress bar
            draw_trails: Draw vehicle movement trails
            max_trail_length: Maximum trail points to display
            show_preview: Show real-time preview window
            
        Returns:
            Dictionary with tracking results and statistics
        """
        if self.model is None:
            raise RuntimeError("Model not loaded!")
        
        # Reset tracking data
        self.track_history.clear()
        self.track_classes.clear()
        self.unique_vehicles.clear()
        self.crossed_vehicles.clear()
        self.counting_line = counting_line
        
        if counting_line:
            print(f"📏 Counting line enabled: {counting_line[0]} -> {counting_line[1]}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📹 Tracking video: {video_path}")
        print(f"   Resolution: {frame_width}x{frame_height}")
        print(f"   FPS: {fps}")
        print(f"   Total frames: {total_frames}")
        
        # Initialize video writer
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (frame_width, frame_height)
            )
        
        # Tracking results
        frame_tracks = []
        vehicle_counts = defaultdict(int)
        
        # Per-minute tracking for time series
        vehicles_per_minute = defaultdict(set)  # minute -> set of vehicle IDs
        crossed_per_minute = defaultdict(set)   # minute -> set of crossed vehicle IDs
        
        frame_idx = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Run tracking
                results = self.model.track(
                    source=frame,
                    conf=self.conf_threshold,
                    iou=self.iou_threshold,
                    classes=VEHICLE_CLASSES,
                    persist=True,  # Persist tracks between frames
                    tracker=self.tracker_config,
                    verbose=False,
                    imgsz=imgsz
                )
                
                # Parse tracking results
                frame_detections = []
                
                if len(results) > 0:
                    result = results[0]
                    
                    if result.boxes is not None and len(result.boxes) > 0:
                        boxes = result.boxes.xyxy.cpu().numpy()
                        confidences = result.boxes.conf.cpu().numpy()
                        class_ids = result.boxes.cls.cpu().numpy().astype(int)
                        
                        # Get track IDs if available
                        track_ids = None
                        if result.boxes.id is not None:
                            track_ids = result.boxes.id.cpu().numpy().astype(int)
                        
                        for idx, (box, conf, cls_id) in enumerate(zip(boxes, confidences, class_ids)):
                            x1, y1, x2, y2 = box
                            center_x = int((x1 + x2) / 2)
                            center_y = int((y1 + y2) / 2)
                            
                            track_id = track_ids[idx] if track_ids is not None else None
                            
                            # Calculate current minute
                            current_minute = int(frame_idx / (fps * 60))
                            
                            # Update tracking history
                            if track_id is not None:
                                # Get previous position for line crossing check
                                prev_pos = None
                                if len(self.track_history[track_id]) > 0:
                                    prev_pos = self.track_history[track_id][-1]
                                
                                current_pos = (center_x, center_y)
                                self.track_history[track_id].append(current_pos)
                                self.track_classes[track_id] = cls_id
                                self.unique_vehicles.add(track_id)
                                
                                # Track vehicle for this minute
                                vehicles_per_minute[current_minute].add(track_id)
                                
                                # Check line crossing
                                if self.counting_line and prev_pos and track_id not in self.crossed_vehicles:
                                    if self._check_line_crossing(prev_pos, current_pos, 
                                                                 self.counting_line[0], 
                                                                 self.counting_line[1]):
                                        self.crossed_vehicles.add(track_id)
                                        crossed_per_minute[current_minute].add(track_id)
                                        print(f"✓ Vehicle {track_id} crossed the line at minute {current_minute}!")
                                
                                # Limit trail length
                                if len(self.track_history[track_id]) > max_trail_length:
                                    self.track_history[track_id].pop(0)
                            
                            detection = {
                                'track_id': int(track_id) if track_id is not None else None,
                                'class_id': int(cls_id),
                                'class_name': get_vehicle_name(cls_id),
                                'confidence': float(conf),
                                'bbox': [float(x) for x in box],
                                'center': (center_x, center_y)
                            }
                            frame_detections.append(detection)
                            
                            # Count vehicles by type
                            if track_id is not None:
                                vehicle_counts[cls_id] += 1
                
                frame_tracks.append({
                    'frame_idx': frame_idx,
                    'timestamp': frame_idx / fps,
                    'tracks': frame_detections
                })
                
                # Draw tracking on frame
                annotated_frame = self._draw_tracks(
                    frame,
                    frame_detections,
                    draw_trails=draw_trails
                )
                
                # Draw counting line if enabled
                if self.counting_line:
                    cv2.line(annotated_frame, 
                            self.counting_line[0], 
                            self.counting_line[1], 
                            (0, 255, 255),  # Yellow line
                            3)
                    # Draw crossing counter
                    text = f"Crossed: {len(self.crossed_vehicles)}"
                    cv2.putText(annotated_frame, text, 
                               (self.counting_line[0][0], self.counting_line[0][1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
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
                    
                    cv2.imshow('TrackFlow - Vehicle Tracking (Press Q to quit)', display_frame)
                    
                    # Check for quit key
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("\n⏸️  Preview window closed by user")
                        break
                
                if show_progress and frame_idx % 30 == 0:
                    progress = (frame_idx / total_frames) * 100
                    crossed_info = f" | Crossed: {len(self.crossed_vehicles)}" if self.counting_line else ""
                    print(f"   Progress: {progress:.1f}% | Unique vehicles: {len(self.unique_vehicles)}{crossed_info}", end='\r')
                
                frame_idx += 1
            
        finally:
            cap.release()
            if writer:
                writer.release()
            if show_preview:
                cv2.destroyAllWindows()
        
        print(f"\n✅ Tracking complete!")
        print(f"   Frames processed: {frame_idx}")
        print(f"   Unique vehicles tracked: {len(self.unique_vehicles)}")
        if self.counting_line:
            print(f"   Vehicles crossed line: {len(self.crossed_vehicles)}")
        
        # Calculate statistics per vehicle type
        vehicle_type_counts = defaultdict(int)
        crossed_type_counts = defaultdict(int)
        
        for track_id in self.unique_vehicles:
            cls_id = self.track_classes.get(track_id)
            if cls_id:
                vehicle_type_counts[cls_id] += 1
                if track_id in self.crossed_vehicles:
                    crossed_type_counts[cls_id] += 1
        
        # Prepare per-minute data for time series
        video_duration_minutes = int(total_frames / (fps * 60)) + 1
        time_series = []
        
        for minute in range(video_duration_minutes):
            vehicles_count = len(vehicles_per_minute.get(minute, set()))
            crossed_count = len(crossed_per_minute.get(minute, set()))
            
            time_series.append({
                'minute': minute,
                'vehicles': vehicles_count,
                'crossed': crossed_count if self.counting_line else None
            })
        
        # Calculate traffic density analysis
        total_minutes = max(1, video_duration_minutes)
        avg_vehicles_per_minute = len(self.unique_vehicles) / total_minutes
        avg_crossed_per_minute = (len(self.crossed_vehicles) / total_minutes) if self.counting_line else None
        
        # Density classification (you can adjust these thresholds)
        if avg_vehicles_per_minute < 5:
            density_level = "Sepi"
            density_percentage = 20
        elif avg_vehicles_per_minute < 15:
            density_level = "Normal"
            density_percentage = 50
        elif avg_vehicles_per_minute < 30:
            density_level = "Ramai"
            density_percentage = 75
        else:
            density_level = "Sangat Padat"
            density_percentage = 95

        # Crossed-only density classification (optional)
        crossed_density_level = None
        crossed_density_percentage = None
        if avg_crossed_per_minute is not None:
            if avg_crossed_per_minute < 3:
                crossed_density_level = "Sepi"
                crossed_density_percentage = 20
            elif avg_crossed_per_minute < 10:
                crossed_density_level = "Normal"
                crossed_density_percentage = 50
            elif avg_crossed_per_minute < 20:
                crossed_density_level = "Ramai"
                crossed_density_percentage = 75
            else:
                crossed_density_level = "Sangat Padat"
                crossed_density_percentage = 95
        
        print(f"   Traffic density (all): {density_level} ({density_percentage}%)")
        print(f"   Avg vehicles/minute: {avg_vehicles_per_minute:.1f}")
        if avg_crossed_per_minute is not None:
            print(f"   Traffic density (crossed): {crossed_density_level} ({crossed_density_percentage}%)")
            print(f"   Avg crossed/minute: {avg_crossed_per_minute:.1f}")
        
        return {
            'video_info': {
                'path': video_path,
                'fps': fps,
                'width': frame_width,
                'height': frame_height,
                'total_frames': total_frames,
                'duration_minutes': video_duration_minutes
            },
            'statistics': {
                'unique_vehicles': len(self.unique_vehicles),
                'vehicles_crossed_line': len(self.crossed_vehicles) if self.counting_line else None,
                'vehicle_type_counts': {
                    get_vehicle_name(cls_id): count 
                    for cls_id, count in vehicle_type_counts.items()
                },
                'crossed_type_counts': {
                    get_vehicle_name(cls_id): count 
                    for cls_id, count in crossed_type_counts.items()
                } if self.counting_line else None,
                'total_detections': sum(len(ft['tracks']) for ft in frame_tracks),
                'time_series': time_series,
                'avg_vehicles_per_minute': round(avg_vehicles_per_minute, 2),
                'density_level': density_level,
                'density_percentage': density_percentage,
                'avg_crossed_per_minute': round(avg_crossed_per_minute, 2) if avg_crossed_per_minute is not None else None,
                'crossed_density_level': crossed_density_level,
                'crossed_density_percentage': crossed_density_percentage
            },
            'frame_tracks': frame_tracks,
            'output_path': output_path
        }
    
    def _draw_tracks(
        self,
        image: np.ndarray,
        tracks: List[Dict[str, Any]],
        draw_trails: bool = True
    ) -> np.ndarray:
        """
        Draw tracking results on image
        
        Args:
            image: Input image
            tracks: List of track detections
            draw_trails: Whether to draw movement trails
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        # Draw trails first (so they appear behind boxes)
        if draw_trails:
            for track in tracks:
                track_id = track.get('track_id')
                if track_id is not None and track_id in self.track_history:
                    points = self.track_history[track_id]
                    
                    # Draw trail as connected lines
                    if len(points) > 1:
                        cls_id = track['class_id']
                        color = COLORS.get(cls_id, (255, 255, 255))
                        
                        for i in range(1, len(points)):
                            # Fade effect: older points are more transparent
                            alpha = i / len(points)
                            thickness = max(1, int(2 * alpha))
                            cv2.line(annotated, points[i-1], points[i], color, thickness)
        
        # Draw bounding boxes and labels
        for track in tracks:
            x1, y1, x2, y2 = track['bbox']
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            class_id = track['class_id']
            class_name = track['class_name']
            confidence = track['confidence']
            track_id = track.get('track_id')
            
            color = COLORS.get(class_id, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Create label with ID
            if track_id is not None:
                label = f"ID:{track_id} {class_name} {confidence:.2f}"
            else:
                label = f"{class_name} {confidence:.2f}"
            
            # Draw label background
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
            
            # Draw center point
            center_x, center_y = track['center']
            cv2.circle(annotated, (center_x, center_y), 3, color, -1)
        
        # Draw statistics overlay
        stats_text = f"Unique Vehicles: {len(self.unique_vehicles)}"
        cv2.putText(
            annotated,
            stats_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )
        
        return annotated
    
    def get_tracking_summary(self) -> Dict[str, Any]:
        """Get summary of tracking results"""
        vehicle_type_counts = defaultdict(int)
        for track_id in self.unique_vehicles:
            cls_id = self.track_classes.get(track_id)
            if cls_id:
                vehicle_type_counts[cls_id] += 1
        
        return {
            'total_unique_vehicles': len(self.unique_vehicles),
            'vehicle_counts': {
                get_vehicle_name(cls_id): count
                for cls_id, count in vehicle_type_counts.items()
            },
            'tracked_ids': sorted(list(self.unique_vehicles))
        }
