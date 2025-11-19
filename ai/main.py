"""
TrackFlow AI - Main Testing Script
Usage: python main.py --source video.mp4 [options]
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.detector import VehicleDetector
from src.tracker import VehicleTracker
from src.utils import (
    validate_video_file,
    get_video_info,
    save_results_json,
    create_detection_summary,
    generate_output_filename
)
from config.settings import (
    OUTPUTS_DIR,
    MODEL_NAME,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    FRAME_SKIP
)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='TrackFlow AI - Vehicle Detection & Tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic detection
  python main.py --source video.mp4
  
  # Detection with tracking
  python main.py --source video.mp4 --track
  
  # Custom output path
  python main.py --source video.mp4 --output results/output.mp4
  
  # Adjust confidence threshold
  python main.py --source video.mp4 --conf 0.4
  
  # Save results as JSON
  python main.py --source video.mp4 --save-json
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        help='Path to input video file'
    )
    
    # Optional arguments
    parser.add_argument(
        '--mode',
        type=str,
        choices=['detect', 'track'],
        default='track',
        help='Operation mode: detect (detection only) or track (detection + tracking)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to output video (default: auto-generated in outputs/)'
    )
    
    parser.add_argument(
        '--conf',
        type=float,
        default=CONFIDENCE_THRESHOLD,
        help=f'Confidence threshold (0-1, default: {CONFIDENCE_THRESHOLD} from .env)'
    )
    
    parser.add_argument(
        '--iou',
        type=float,
        default=IOU_THRESHOLD,
        help=f'IOU threshold for NMS (0-1, default: {IOU_THRESHOLD} from .env)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=MODEL_NAME,
        choices=['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt'],
        help=f'YOLOv8 model size (default: {MODEL_NAME} from .env)'
    )
    
    parser.add_argument(
        '--no-trails',
        action='store_true',
        help='Disable movement trails in tracking mode'
    )
    
    parser.add_argument(
        '--imgsz',
        type=int,
        default=640,
        help='Inference image size (lower = faster, higher = more accurate). Typical: 512, 640, 960, 1280'
    )
    
    parser.add_argument(
        '--frame-skip',
        type=int,
        default=FRAME_SKIP,
        help='Process every Nth frame (1=all frames). Higher values increase speed.'
    )
    
    parser.add_argument(
        '--show-preview',
        action='store_true',
        help='Show real-time preview window during processing (Press Q to quit)'
    )
    
    parser.add_argument(
        '--save-json',
        action='store_true',
        help='Save results as JSON file'
    )
    
    parser.add_argument(
        '--no-video',
        action='store_true',
        help='Skip video output (only process and save JSON)'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show video info and exit (no processing)'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("\n" + "="*60)
    print("🚗 TRACKFLOW AI - Vehicle Detection & Tracking")
    print("="*60 + "\n")
    
    # Validate input video
    print(f"📂 Checking input video: {args.source}")
    is_valid, error_msg = validate_video_file(args.source)
    
    if not is_valid:
        print(f"❌ Error: {error_msg}")
        return 1
    
    print("✅ Video file valid\n")
    
    # Show video info
    video_info = get_video_info(args.source)
    print("📹 Video Information:")
    print(f"   Filename: {video_info['filename']}")
    print(f"   Resolution: {video_info['width']}x{video_info['height']}")
    print(f"   FPS: {video_info['fps']}")
    print(f"   Total Frames: {video_info['total_frames']}")
    print(f"   Duration: {video_info['duration_seconds']:.2f}s")
    print(f"   File Size: {video_info['file_size_mb']:.2f} MB\n")
    
    if args.info:
        return 0
    
    # Generate output path if not specified
    output_path = args.output
    if output_path is None and not args.no_video:
        suffix = "_tracked" if args.mode == 'track' else "_detected"
        output_path = generate_output_filename(args.source, suffix=suffix)
    
    # Process video
    results = None
    
    if args.mode == 'track':
        # Tracking mode
        print(f"🎯 Mode: Detection + Tracking")
        print(f"   Model: {args.model}")
        print(f"   Confidence: {args.conf}")
        print(f"   Trails: {'Disabled' if args.no_trails else 'Enabled'}")
        print(f"   Image Size: {args.imgsz}")
        print(f"   Frame Skip: {args.frame_skip}")
        print(f"   Preview: {'Enabled (Press Q to quit)' if args.show_preview else 'Disabled'}\n")
        
        tracker = VehicleTracker(
            model_name=args.model,
            conf_threshold=args.conf,
            iou_threshold=args.iou
        )
        
        results = tracker.track_video(
            video_path=args.source,
            output_path=output_path if not args.no_video else None,
            show_progress=True,
            draw_trails=not args.no_trails,
            show_preview=args.show_preview,
            imgsz=args.imgsz
        )
        
    else:
        # Detection only mode
        print(f"🔍 Mode: Detection Only")
        print(f"   Model: {args.model}")
        print(f"   Confidence: {args.conf}")
        print(f"   Image Size: {args.imgsz}")
        print(f"   Frame Skip: {args.frame_skip}")
        print(f"   Preview: {'Enabled (Press Q to quit)' if args.show_preview else 'Disabled'}\n")
        
        detector = VehicleDetector(
            model_name=args.model,
            conf_threshold=args.conf,
            iou_threshold=args.iou
        )
        
        results = detector.detect_video(
            video_path=args.source,
            output_path=output_path if not args.no_video else None,
            show_progress=True,
            show_preview=args.show_preview,
            frame_skip=args.frame_skip,
            imgsz=args.imgsz
        )
    
    # Print summary
    print("\n" + create_detection_summary(results))
    
    # Save JSON if requested
    if args.save_json:
        json_path = generate_output_filename(args.source, suffix="_results", extension=".json")
        save_results_json(results, json_path)
        print(f"\n💾 Results saved to: {json_path}")
    
    print("\n✅ Processing complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
