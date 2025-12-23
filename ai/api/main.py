# TrackFlow API - FastAPI endpoints for vehicle detection & tracking

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import shutil
import uuid
import asyncio

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detector import VehicleDetector
from src.tracker import VehicleTracker
from src.utils import (
    validate_video_file,
    get_video_info,
    save_results_json,
    generate_output_filename
)
from config.settings import OUTPUTS_DIR, MAX_VIDEO_SIZE_MB, SUPPORTED_FORMATS


# Initialize FastAPI app
app = FastAPI(
    title="TrackFlow API",
    description="Vehicle Detection & Tracking API using YOLOv8 + COCO",
    version="1.0.0"
)

# CORS middleware (configurable for deployment)
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = ["*"] if allowed_origins_env.strip() == "*" else [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models (lazy loading)
detector = None
tracker = None

# Global tasks storage (in-memory for now)
tasks: Dict[str, Dict[str, Any]] = {}


# Request/Response models
class ProcessRequest(BaseModel):
    """Request model for video processing"""
    mode: str = Field(default="track", description="Processing mode: 'detect' or 'track'")
    confidence: float = Field(default=0.25, ge=0.0, le=1.0, description="Confidence threshold")
    save_video: bool = Field(default=True, description="Save output video")
    draw_trails: bool = Field(default=True, description="Draw movement trails (track mode only)")


class VideoInfoResponse(BaseModel):
    """Response model for video info"""
    filename: str
    fps: int
    width: int
    height: int
    total_frames: int
    duration_seconds: float
    file_size_mb: float


class ProcessResponse(BaseModel):
    """Response model for processing results"""
    status: str
    message: str
    video_info: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    output_video_path: Optional[str] = None
    results_json_path: Optional[str] = None


def get_detector() -> VehicleDetector:
    """Get or initialize detector"""
    global detector
    if detector is None:
        detector = VehicleDetector()
    return detector


def get_tracker() -> VehicleTracker:
    """Get or initialize tracker"""
    global tracker
    if tracker is None:
        tracker = VehicleTracker()
    return tracker


def cleanup_temp_file(file_path: str):
    """Background task to cleanup temporary files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up {file_path}: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TrackFlow API - Vehicle Detection & Tracking",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "process": "/process",
            "results": "/results/{job_id}",
            "download": "/download/{filename}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "detector": detector is not None,
            "tracker": tracker is not None
        }
    }


@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Upload video file for processing
    
    Args:
        file: Video file to upload
        
    Returns:
        Upload status and video information
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower().replace('.', '')
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Format not supported. Use: {', '.join(SUPPORTED_FORMATS)}"
        )
    
    # Save uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"upload_{timestamp}_{file.filename}"
    temp_path = OUTPUTS_DIR / "uploads" / temp_filename
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Save file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check file size
        file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
        if file_size_mb > MAX_VIDEO_SIZE_MB:
            os.remove(temp_path)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {MAX_VIDEO_SIZE_MB} MB"
            )
        
        # Validate video
        is_valid, error_msg = validate_video_file(str(temp_path))
        if not is_valid:
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Get video info
        video_info = get_video_info(str(temp_path))
        
        return {
            "status": "success",
            "message": "Video uploaded successfully",
            "file_path": str(temp_path),
            "video_info": video_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if temp_path.exists():
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/process")
async def process_video_async(
    file: UploadFile = File(...),
    mode: str = "track",
    confidence: float = 0.25,
    save_video: bool = True,
    draw_trails: bool = True,
    line_x1: Optional[int] = None,
    line_y1: Optional[int] = None,
    line_x2: Optional[int] = None,
    line_y2: Optional[int] = None,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Process video for vehicle detection/tracking (ASYNC - returns immediately)
    
    Args:
        file: Video file to process
        mode: Processing mode ('detect' or 'track')
        confidence: Confidence threshold (0-1)
        save_video: Save output video
        draw_trails: Draw movement trails (track mode only)
        line_x1, line_y1, line_x2, line_y2: Counting line coordinates (optional)
        
    Returns:
        Task ID for checking status
    """
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Upload file first
    upload_result = await upload_video(file)
    temp_path = upload_result["file_path"]
    
    # Initialize task
    tasks[task_id] = {
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "video_path": temp_path,
        "progress": 0
    }
    
    # Start background processing
    background_tasks.add_task(
        process_video_background,
        task_id,
        temp_path,
        mode,
        confidence,
        save_video,
        draw_trails,
        line_x1,
        line_y1,
        line_x2,
        line_y2
    )
    
    # Return immediately
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Video processing started in background"
    }


def process_video_background(
    task_id: str,
    temp_path: str,
    mode: str,
    confidence: float,
    save_video: bool,
    draw_trails: bool,
    line_x1: Optional[int],
    line_y1: Optional[int],
    line_x2: Optional[int],
    line_y2: Optional[int]
):
    """Background task to process video"""
    try:
        # Generate output path
        output_path = None
        if save_video:
            suffix = "_tracked" if mode == "track" else "_detected"
            output_path = generate_output_filename(temp_path, suffix=suffix)
        
        # Parse counting line if provided
        counting_line = None
        if all(v is not None for v in [line_x1, line_y1, line_x2, line_y2]):
            counting_line = ((line_x1, line_y1), (line_x2, line_y2))
            print(f"📏 [{task_id}] Counting line provided: {counting_line}")
        
        # Process based on mode
        results = None
        
        if mode == "track":
            # Tracking mode
            tracker_instance = get_tracker()
            tracker_instance.conf_threshold = confidence
            
            results = tracker_instance.track_video(
                video_path=temp_path,
                output_path=output_path,
                counting_line=counting_line,
                show_progress=False,
                draw_trails=draw_trails
            )
            
        elif mode == "detect":
            # Detection mode
            detector_instance = get_detector()
            detector_instance.conf_threshold = confidence
            
            results = detector_instance.detect_video(
                video_path=temp_path,
                output_path=output_path,
                show_progress=False
            )
        
        # Save results as JSON
        json_path = generate_output_filename(temp_path, suffix="_results", extension=".json")
        save_results_json(results, json_path)
        
        # Update task status
        tasks[task_id] = {
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "video_info": results.get("video_info"),
            "statistics": results.get("statistics"),
            "output_video_path": output_path,
            "results_json_path": json_path,
            "progress": 100
        }
        
        # Cleanup temp file
        cleanup_temp_file(temp_path)
        
        print(f"✅ [{task_id}] Processing completed successfully")
        
    except Exception as e:
        print(f"❌ [{task_id}] Processing failed: {str(e)}")
        tasks[task_id] = {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }
        # Cleanup temp file on error
        cleanup_temp_file(temp_path)


@app.get("/task/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a processing task
    
    Args:
        task_id: Task ID from process endpoint
        
    Returns:
        Task status and results (if completed)
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download output file
    
    Args:
        filename: Name of file to download
        
    Returns:
        File response
    """
    file_path = OUTPUTS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )


@app.get("/results/{job_id}")
async def get_results(job_id: str):
    """
    Get processing results by job ID
    
    Args:
        job_id: Job identifier
        
    Returns:
        Processing results
    """
    # This is a placeholder - implement actual job tracking if needed
    raise HTTPException(
        status_code=501,
        detail="Job tracking not implemented. Use /download endpoint for results."
    )


@app.get("/models")
async def get_models_info():
    """Get information about loaded models"""
    info = {
        "detector": None,
        "tracker": None
    }
    
    if detector is not None:
        info["detector"] = detector.get_model_info()
    
    if tracker is not None:
        info["tracker"] = {
            "model_name": tracker.model_name,
            "confidence_threshold": tracker.conf_threshold,
            "tracker_config": tracker.tracker_config
        }
    
    return info


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚗 TRACKFLOW API SERVER")
    print("="*60)
    print(f"\nStarting server at http://localhost:8000")
    print(f"API docs at http://localhost:8000/docs")
    print(f"Alternative docs at http://localhost:8000/redoc\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
