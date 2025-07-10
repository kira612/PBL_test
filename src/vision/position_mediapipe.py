# -*- coding: utf-8 -*-
"""
MediaPipe pose estimation based position estimation.
(MediaPipeポーズ推定ベースの位置推定)
"""

import time
from typing import Optional

import cv2
import numpy as np
from loguru import logger

from ..core.detector import Detection
from ..core.position_interface import FrameBasedPositionEstimator, RoomPosition, RoomDimensions

# Optional imports for MediaPipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("MediaPipe not available. Install with: pip install mediapipe")


class MediaPipePoseEstimator(FrameBasedPositionEstimator):
    """
    Position estimator using MediaPipe pose estimation.
    (MediaPipeポーズ推定を使用した位置推定器)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize MediaPipe pose estimator.
        (MediaPipeポーズ推定器の初期化)
        
        Args:
            room_dimensions: Room dimensions (部屋の寸法)
            frame_width: Frame width in pixels (フレーム幅)
            frame_height: Frame height in pixels (フレーム高さ)
        """
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError("MediaPipe is required but not installed. Run: pip install mediapipe")
        
        super().__init__(room_dimensions, frame_width, frame_height)
        
        # Initialize MediaPipe pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Camera parameters for perspective correction
        self.camera_height = room_dimensions.camera_height
        self.camera_focal_length = 500  # Estimated focal length
        
        # Simple coordinate mapping (can be improved with calibration)
        self.x_scale = room_dimensions.width / frame_width
        self.y_scale = room_dimensions.height / frame_height
    
    @property
    def method_name(self) -> str:
        """Name of the estimation method."""
        return "mediapipe_pose"
    
    def _estimate_with_frame(self, detection: Detection, frame: np.ndarray) -> Optional[RoomPosition]:
        """
        Estimate room position using MediaPipe pose landmarks.
        (MediaPipeポーズランドマークを使用した部屋座標での位置推定)
        
        Args:
            detection: Person detection result (人物検出結果)
            frame: Input frame for pose estimation (ポーズ推定用の入力フレーム)
            
        Returns:
            Optional[RoomPosition]: Estimated room position or None (推定された部屋座標での位置またはNone)
        """
        try:
            # Extract person region from detection
            x, y, w, h = detection.bbox
            person_roi = frame[y:y+h, x:x+w]
            
            if person_roi.size == 0:
                return None
            
            # Convert BGR to RGB for MediaPipe
            rgb_roi = cv2.cvtColor(person_roi, cv2.COLOR_BGR2RGB)
            
            # Process pose estimation
            results = self.pose.process(rgb_roi)
            
            if not results.pose_landmarks:
                # Fallback to bbox center if pose not detected
                return self._fallback_estimation(detection)
            
            # Get ankle landmarks (closest to ground contact points)
            landmarks = results.pose_landmarks.landmark
            left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
            
            # Use the ankle with higher confidence (lower y-value in image)
            if left_ankle.visibility > right_ankle.visibility:
                ankle_x = left_ankle.x * w + x  # Convert to frame coordinates
                ankle_y = left_ankle.y * h + y
                confidence_factor = left_ankle.visibility
            else:
                ankle_x = right_ankle.x * w + x
                ankle_y = right_ankle.y * h + y
                confidence_factor = right_ankle.visibility
            
            # Convert foot position to room coordinates
            room_x = ankle_x * self.x_scale
            room_y = ankle_y * self.y_scale
            
            # Apply perspective correction based on y-position
            # Objects farther from camera appear higher in image
            depth_factor = 1.0 - (ankle_y / self.frame_height) * 0.3
            room_y = room_y * depth_factor
            
            # Clamp to room boundaries
            room_x = max(0, min(room_x, self.room_dimensions.width))
            room_y = max(0, min(room_y, self.room_dimensions.height))
            
            confidence = detection.confidence * confidence_factor * 0.95
            
            return RoomPosition(
                x=room_x,
                y=room_y,
                confidence=confidence,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"MediaPipe pose estimation failed: {e}")
            return self._fallback_estimation(detection)
    
    def _fallback_estimation(self, detection: Detection) -> RoomPosition:
        """
        Fallback to simple bbox-based estimation.
        (シンプルなバウンディングボックスベースの推定へのフォールバック)
        """
        center_x, center_y = detection.center
        room_x = center_x * self.x_scale
        room_y = center_y * self.y_scale
        
        return RoomPosition(
            x=room_x,
            y=room_y,
            confidence=detection.confidence * 0.6,  # Lower confidence for fallback
            timestamp=time.time()
        )