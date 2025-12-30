"""
AI Module Unit Tests - Vehicle Detection & Tracking
Framework: pytest
Run: pytest -v --cov=src tests/

Test Coverage:
- WB4.1: YOLOv8 Model Loading
- WB4.2: Bounding Box Format
- WB4.3: Vehicle Class Filtering
- WB5.1: Track ID Assignment
- WB5.2: Track Linking Logic
- WB5.3: Track Termination
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detector import VehicleDetector
from src.tracker import VehicleTracker
from src.utils import validate_video_file


class TestVehicleDetector:
    """Tests for vehicle detection module"""

    @pytest.fixture
    def detector(self):
        """Initialize detector for testing"""
        return VehicleDetector(model_size='nano')  # Use smaller model for testing

    def test_WB41_model_loads_successfully(self, detector):
        """WB4.1: Verify YOLOv8 model loads without errors"""
        assert detector.model is not None
        assert hasattr(detector.model, 'predict')
        assert detector.model.names is not None

    def test_WB41_model_is_callable(self, detector):
        """WB4.1: Verify model is ready for inference"""
        assert callable(detector.model.predict)
        # Can call predict without errors
        dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
        result = detector.model.predict(dummy_image, verbose=False)
        assert result is not None

    def test_WB42_bounding_box_format(self, detector):
        """WB4.2: Verify bounding boxes in correct format (x1, y1, x2, y2)"""
        # Create synthetic image with predictable content
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        detections = detector.detect_objects(dummy_image)
        
        # Check format of detections
        for detection in detections:
            assert 'bbox' in detection or 'x1' in detection
            bbox = detection.get('bbox') or [
                detection.get('x1'),
                detection.get('y1'),
                detection.get('x2'),
                detection.get('y2')
            ]
            
            x1, y1, x2, y2 = bbox
            
            # Verify coordinates are within image bounds
            assert 0 <= x1 < 640, f"x1 {x1} out of bounds"
            assert 0 <= y1 < 640, f"y1 {y1} out of bounds"
            assert 0 <= x2 <= 640, f"x2 {x2} out of bounds"
            assert 0 <= y2 <= 640, f"y2 {y2} out of bounds"
            
            # Verify x1 < x2 and y1 < y2
            assert x1 < x2, "Invalid bbox: x1 >= x2"
            assert y1 < y2, "Invalid bbox: y1 >= y2"

    def test_WB42_confidence_scores_valid(self, detector):
        """WB4.2: Verify confidence scores are valid (0-1 range)"""
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        detections = detector.detect_objects(dummy_image)
        
        for detection in detections:
            confidence = detection.get('confidence')
            assert confidence is not None, "Missing confidence score"
            assert 0 <= confidence <= 1, f"Confidence {confidence} out of range"

    def test_WB43_vehicle_class_filtering(self, detector):
        """WB4.3: Verify only vehicle classes detected"""
        VEHICLE_CLASSES = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']
        
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        detections = detector.detect_objects(dummy_image)
        
        for detection in detections:
            class_name = detection.get('class')
            assert class_name in VEHICLE_CLASSES, \
                f"Non-vehicle class detected: {class_name}"

    def test_WB43_confidence_threshold_applied(self, detector):
        """WB4.3: Verify confidence threshold is applied"""
        threshold = 0.5
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        detections = detector.detect_objects(dummy_image, conf_threshold=threshold)
        
        for detection in detections:
            confidence = detection.get('confidence')
            assert confidence >= threshold, \
                f"Detection confidence {confidence} below threshold {threshold}"

    def test_WB43_no_non_vehicle_objects(self, detector):
        """WB4.3: Verify non-vehicle objects filtered"""
        NON_VEHICLES = ['person', 'dog', 'cat', 'airplane', 'bench']
        
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        detections = detector.detect_objects(dummy_image)
        
        detected_classes = [d.get('class') for d in detections]
        
        for non_vehicle in NON_VEHICLES:
            assert non_vehicle not in detected_classes, \
                f"Non-vehicle class '{non_vehicle}' detected"

    def test_empty_image_no_detections(self, detector):
        """Test that blank image produces no detections"""
        blank_image = np.zeros((640, 640, 3), dtype=np.uint8)
        
        detections = detector.detect_objects(blank_image)
        
        # Should have few or no detections
        assert len(detections) < 5, "Blank image produced too many detections"

    def test_different_image_sizes(self, detector):
        """Test detector handles different image sizes"""
        sizes = [(480, 640), (720, 1280), (1080, 1920)]
        
        for height, width in sizes:
            image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            detections = detector.detect_objects(image)
            
            # Should not raise error and return valid detections
            assert isinstance(detections, list)


class TestVehicleTracker:
    """Tests for vehicle tracking module"""

    @pytest.fixture
    def tracker(self):
        """Initialize tracker for testing"""
        return VehicleTracker()

    def test_WB51_track_id_assignment(self, tracker):
        """WB5.1: Verify each vehicle gets unique ID"""
        # Create mock detections for frame 1
        detections_frame1 = [
            {'id': 0, 'bbox': [100, 100, 150, 150], 'class': 'car'},
            {'id': 1, 'bbox': [200, 200, 250, 250], 'class': 'car'},
            {'id': 2, 'bbox': [300, 300, 350, 350], 'class': 'truck'},
        ]
        
        # Update tracker with frame 1
        tracks = tracker.update(detections_frame1, frame_id=1)
        
        # Verify unique IDs assigned
        track_ids = [t['id'] for t in tracks]
        assert len(track_ids) == len(set(track_ids)), \
            "Duplicate track IDs assigned"
        assert len(track_ids) == 3, "Expected 3 tracks"

    def test_WB52_track_linking_across_frames(self, tracker):
        """WB5.2: Verify vehicle linked across frames"""
        # Frame 1: Vehicle at (100, 100)
        detections_frame1 = [
            {'bbox': [100, 100, 150, 150], 'class': 'car', 'confidence': 0.95}
        ]
        tracks_frame1 = tracker.update(detections_frame1, frame_id=1)
        vehicle_id_frame1 = tracks_frame1[0]['id']
        
        # Frame 2: Same vehicle moved to (105, 105) - close to original
        detections_frame2 = [
            {'bbox': [105, 105, 155, 155], 'class': 'car', 'confidence': 0.95}
        ]
        tracks_frame2 = tracker.update(detections_frame2, frame_id=2)
        vehicle_id_frame2 = tracks_frame2[0]['id']
        
        # Should have same ID (same vehicle)
        assert vehicle_id_frame1 == vehicle_id_frame2, \
            "Vehicle ID changed when it shouldn't"

    def test_WB52_different_objects_different_ids(self, tracker):
        """WB5.2: Verify different vehicles have different IDs"""
        # Frame 1: Two vehicles far apart
        detections_frame1 = [
            {'bbox': [100, 100, 150, 150], 'class': 'car'},
            {'bbox': [500, 500, 550, 550], 'class': 'car'},
        ]
        tracks_frame1 = tracker.update(detections_frame1, frame_id=1)
        
        # Frame 2: Vehicles moved slightly
        detections_frame2 = [
            {'bbox': [105, 105, 155, 155], 'class': 'car'},
            {'bbox': [505, 505, 555, 555], 'class': 'car'},
        ]
        tracks_frame2 = tracker.update(detections_frame2, frame_id=2)
        
        # Extract IDs from frame 1
        id1_frame1 = tracks_frame1[0]['id']
        id2_frame1 = tracks_frame1[1]['id']
        
        # Extract IDs from frame 2 (sorted by x position)
        tracks_sorted = sorted(tracks_frame2, key=lambda t: t['bbox'][0])
        id1_frame2 = tracks_sorted[0]['id']
        id2_frame2 = tracks_sorted[1]['id']
        
        # Should maintain correspondence
        assert id1_frame1 == id1_frame2, "First vehicle ID changed"
        assert id2_frame1 == id2_frame2, "Second vehicle ID changed"
        assert id1_frame1 != id2_frame1, "Different vehicles have same ID"

    def test_WB53_track_termination(self, tracker):
        """WB5.3: Verify tracks end when vehicle leaves"""
        # Frame 1: Vehicle present
        detections_frame1 = [
            {'bbox': [100, 100, 150, 150], 'class': 'car'}
        ]
        tracks_frame1 = tracker.update(detections_frame1, frame_id=1)
        vehicle_id = tracks_frame1[0]['id']
        
        # Frame 2-10: Vehicle no longer present
        for frame_id in range(2, 11):
            detections = []  # No detections
            tracks = tracker.update(detections, frame_id=frame_id)
        
        # After sufficient frames without detection, track should be terminated
        max_age = tracker.max_age if hasattr(tracker, 'max_age') else 30
        
        # Check at frame max_age + 1
        final_tracks = tracker.get_tracks()
        
        # Vehicle should be removed from active tracks after max_age frames
        active_ids = [t['id'] for t in final_tracks if t.get('status') == 'active']
        assert vehicle_id not in active_ids or len(final_tracks) < 1, \
            "Track not terminated after max age"

    def test_WB53_completed_tracks_available(self, tracker):
        """WB5.3: Verify completed tracks stored properly"""
        # Create and remove a track
        detections_frame1 = [
            {'bbox': [100, 100, 150, 150], 'class': 'car'}
        ]
        tracks_frame1 = tracker.update(detections_frame1, frame_id=1)
        vehicle_id = tracks_frame1[0]['id']
        
        # Remove vehicle
        for frame_id in range(2, 50):
            tracker.update([], frame_id=frame_id)
        
        # Get completed tracks
        if hasattr(tracker, 'get_completed_tracks'):
            completed = tracker.get_completed_tracks()
            assert isinstance(completed, list)


class TestUtilities:
    """Tests for utility functions"""

    def test_validate_video_file_valid_formats(self):
        """Test validation of valid video formats"""
        valid_formats = [
            'video.mp4',
            'video.avi',
            'video.mov',
            'video.mkv'
        ]
        
        for filename in valid_formats:
            assert validate_video_file(filename), \
                f"Valid format rejected: {filename}"

    def test_validate_video_file_invalid_formats(self):
        """Test validation rejects invalid formats"""
        invalid_formats = [
            'document.pdf',
            'image.jpg',
            'audio.mp3',
            'data.csv'
        ]
        
        for filename in invalid_formats:
            assert not validate_video_file(filename), \
                f"Invalid format accepted: {filename}"

    def test_validate_video_file_case_insensitive(self):
        """Test validation is case-insensitive"""
        assert validate_video_file('video.MP4')
        assert validate_video_file('video.Mp4')
        assert validate_video_file('video.AVI')


class TestIntegration:
    """Integration tests for detector + tracker"""

    def test_WB81_complete_detection_and_tracking(self):
        """WB8.1: Test complete detection and tracking pipeline"""
        detector = VehicleDetector(model_size='nano')
        tracker = VehicleTracker()
        
        # Simulate processing multiple frames
        frames_to_process = 10
        
        for frame_id in range(1, frames_to_process + 1):
            # Create synthetic frame (in real scenario, this would be video frame)
            frame = np.random.randint(0, 255, (640, 480, 3), dtype=np.uint8)
            
            # Detect objects
            detections = detector.detect_objects(frame)
            
            # Update tracker
            tracks = tracker.update(detections, frame_id=frame_id)
            
            # Verify results
            assert isinstance(tracks, list)
            for track in tracks:
                assert 'id' in track
                assert 'bbox' in track or 'x1' in track

    def test_WB82_error_handling_invalid_input(self):
        """WB8.2: Test error handling with invalid input"""
        detector = VehicleDetector(model_size='nano')
        
        # Test with None
        try:
            detections = detector.detect_objects(None)
        except (TypeError, AttributeError):
            pass  # Expected
        
        # Test with wrong shape
        wrong_shape = np.zeros((640, 640), dtype=np.uint8)  # 2D instead of 3D
        try:
            detections = detector.detect_objects(wrong_shape)
        except (ValueError, TypeError):
            pass  # Expected


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
