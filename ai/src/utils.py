"""
Utility functions for TrackFlow AI
"""
import os
import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from config.settings import OUTPUTS_DIR, SUPPORTED_FORMATS


def validate_video_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate video file
    
    Args:
        file_path: Path to video file
        
    Returns:
        (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, "File tidak ditemukan"
    
    file_ext = Path(file_path).suffix.lower().replace('.', '')
    if file_ext not in SUPPORTED_FORMATS:
        return False, f"Format tidak didukung. Gunakan: {', '.join(SUPPORTED_FORMATS)}"
    
    # Try to open video
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        cap.release()
        return False, "Tidak dapat membuka file video"
    
    # Check if video has frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    if total_frames == 0:
        return False, "Video tidak memiliki frame"
    
    return True, ""


def get_video_info(video_path: str) -> Dict[str, Any]:
    """
    Get video metadata
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video information
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    info = {
        'path': video_path,
        'filename': Path(video_path).name,
        'fps': int(cap.get(cv2.CAP_PROP_FPS)),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'duration_seconds': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / int(cap.get(cv2.CAP_PROP_FPS)),
        'file_size_mb': os.path.getsize(video_path) / (1024 * 1024)
    }
    
    cap.release()
    return info


def save_results_json(results: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Save detection/tracking results to JSON file
    
    Args:
        results: Results dictionary
        output_path: Output JSON path (optional)
        
    Returns:
        Path to saved JSON file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUTS_DIR / f"results_{timestamp}.json"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return str(output_path)


def extract_frames(
    video_path: str,
    output_dir: str,
    frame_indices: Optional[List[int]] = None,
    interval: Optional[int] = None
) -> List[str]:
    """
    Extract frames from video
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save frames
        frame_indices: Specific frame indices to extract (optional)
        interval: Extract every Nth frame (optional)
        
    Returns:
        List of saved frame paths
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_frames = []
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        should_save = False
        
        if frame_indices is not None:
            should_save = frame_idx in frame_indices
        elif interval is not None:
            should_save = frame_idx % interval == 0
        
        if should_save:
            frame_path = output_path / f"frame_{frame_idx:06d}.jpg"
            cv2.imwrite(str(frame_path), frame)
            saved_frames.append(str(frame_path))
        
        frame_idx += 1
    
    cap.release()
    return saved_frames


def resize_video(
    input_path: str,
    output_path: str,
    target_width: int = 640,
    maintain_aspect: bool = True
) -> str:
    """
    Resize video to target dimensions
    
    Args:
        input_path: Input video path
        output_path: Output video path
        target_width: Target width in pixels
        maintain_aspect: Maintain aspect ratio
        
    Returns:
        Output video path
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {input_path}")
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Calculate new dimensions
    if maintain_aspect:
        aspect_ratio = height / width
        target_height = int(target_width * aspect_ratio)
    else:
        target_height = height
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        resized = cv2.resize(frame, (target_width, target_height))
        writer.write(resized)
    
    cap.release()
    writer.release()
    
    return output_path


def format_time(seconds: float) -> str:
    """
    Format seconds to HH:MM:SS
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def create_detection_summary(results: Dict[str, Any]) -> str:
    """
    Create human-readable summary of detection results
    
    Args:
        results: Detection/tracking results
        
    Returns:
        Formatted summary string
    """
    summary_lines = []
    summary_lines.append("=" * 50)
    summary_lines.append("🚗 TRACKFLOW - HASIL DETEKSI KENDARAAN")
    summary_lines.append("=" * 50)
    
    # Video info
    if 'video_info' in results:
        info = results['video_info']
        summary_lines.append("\n📹 INFORMASI VIDEO:")
        summary_lines.append(f"   File: {Path(info['path']).name}")
        summary_lines.append(f"   Resolusi: {info['width']}x{info['height']}")
        summary_lines.append(f"   FPS: {info['fps']}")
        summary_lines.append(f"   Total Frame: {info['total_frames']}")
        if 'processed_frames' in info:
            summary_lines.append(f"   Frame Diproses: {info['processed_frames']}")
    
    # Statistics
    if 'statistics' in results:
        stats = results['statistics']
        summary_lines.append("\n📊 STATISTIK DETEKSI:")
        
        if 'unique_vehicles' in stats:
            summary_lines.append(f"   Total Kendaraan Unik: {stats['unique_vehicles']}")
        
        if 'total_detections' in stats:
            summary_lines.append(f"   Total Deteksi: {stats['total_detections']}")
        
        if 'vehicle_counts' in stats or 'vehicle_type_counts' in stats:
            counts = stats.get('vehicle_counts') or stats.get('vehicle_type_counts')
            summary_lines.append("\n   Rincian per Jenis Kendaraan:")
            for vehicle_type, count in counts.items():
                summary_lines.append(f"      • {vehicle_type}: {count}")
        
        if 'average_per_frame' in stats:
            summary_lines.append(f"\n   Rata-rata Deteksi per Frame: {stats['average_per_frame']:.2f}")
    
    # Output info
    if 'output_path' in results and results['output_path']:
        summary_lines.append(f"\n💾 Output Video: {results['output_path']}")
    
    summary_lines.append("\n" + "=" * 50)
    
    return "\n".join(summary_lines)


def generate_output_filename(
    input_path: str,
    suffix: str = "_tracked",
    extension: str = ".mp4"
) -> str:
    """
    Generate output filename based on input
    
    Args:
        input_path: Input file path
        suffix: Suffix to add to filename
        extension: Output file extension
        
    Returns:
        Output file path
    """
    input_path = Path(input_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_name = f"{input_path.stem}{suffix}_{timestamp}{extension}"
    output_path = OUTPUTS_DIR / output_name
    
    return str(output_path)


def calculate_iou(box1: List[float], box2: List[float]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes
    
    Args:
        box1: [x1, y1, x2, y2]
        box2: [x1, y1, x2, y2]
        
    Returns:
        IoU value (0-1)
    """
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    # Calculate intersection area
    intersect_x_min = max(x1_min, x2_min)
    intersect_y_min = max(y1_min, y2_min)
    intersect_x_max = min(x1_max, x2_max)
    intersect_y_max = min(y1_max, y2_max)
    
    if intersect_x_max < intersect_x_min or intersect_y_max < intersect_y_min:
        return 0.0
    
    intersect_area = (intersect_x_max - intersect_x_min) * (intersect_y_max - intersect_y_min)
    
    # Calculate union area
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = box1_area + box2_area - intersect_area
    
    return intersect_area / union_area if union_area > 0 else 0.0


def draw_info_overlay(
    image: np.ndarray,
    info_text: List[str],
    position: Tuple[int, int] = (10, 30),
    font_scale: float = 0.6,
    color: Tuple[int, int, int] = (0, 255, 0),
    bg_color: Optional[Tuple[int, int, int]] = (0, 0, 0),
    bg_alpha: float = 0.5
) -> np.ndarray:
    """
    Draw text overlay on image with optional background
    
    Args:
        image: Input image
        info_text: List of text lines to display
        position: Starting position (x, y)
        font_scale: Font scale
        color: Text color (BGR)
        bg_color: Background color (BGR), None for no background
        bg_alpha: Background transparency (0-1)
        
    Returns:
        Image with overlay
    """
    annotated = image.copy()
    x, y = position
    line_height = 30
    
    # Draw background if specified
    if bg_color is not None:
        max_width = max(cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)[0][0] 
                       for text in info_text)
        padding = 10
        
        overlay = annotated.copy()
        cv2.rectangle(
            overlay,
            (x - padding, y - 25),
            (x + max_width + padding, y + len(info_text) * line_height),
            bg_color,
            -1
        )
        cv2.addWeighted(overlay, bg_alpha, annotated, 1 - bg_alpha, 0, annotated)
    
    # Draw text
    for i, text in enumerate(info_text):
        text_y = y + i * line_height
        cv2.putText(
            annotated,
            text,
            (x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            2,
            cv2.LINE_AA
        )
    
    return annotated
