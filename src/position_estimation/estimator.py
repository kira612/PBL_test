# -*- coding: utf-8 -*-
"""
Position estimation module for 3m x 4m laboratory room.
(3m x 4m研究室での位置推定モジュール)
"""

import math
import time
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from loguru import logger

from ..detection.detector import Detection

# Optional imports for advanced features
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("MediaPipe not available. Install with: pip install mediapipe")

try:
    import torch
    import torchvision.transforms as transforms
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Install with: pip install torch torchvision")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Install with: pip install transformers")


class PositionMethod(Enum):
    """Position estimation method enumeration."""
    BBOX_CENTER = "bbox_center"
    PERSPECTIVE_MAPPING = "perspective_mapping"
    DEPTH_ESTIMATION = "depth_estimation"
    MEDIAPIPE_POSE = "mediapipe_pose"
    MIDAS_DEPTH = "midas_depth"
    DPT_DEPTH = "dpt_depth"


@dataclass
class RoomPosition:
    """
    Position in the laboratory room coordinate system.
    (研究室内の座標系での位置)
    """
    x: float  # meters from left wall (左壁からの距離)
    y: float  # meters from front wall (前壁からの距離)
    confidence: float  # position confidence (位置の信頼度)
    timestamp: float
    
    def distance_to(self, other: 'RoomPosition') -> float:
        """Calculate distance to another position."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class RoomDimensions:
    """
    Laboratory room dimensions.
    (研究室の寸法)
    """
    width: float = 4.0  # meters (width: 4m)
    height: float = 3.0  # meters (depth: 3m)
    camera_height: float = 2.5  # meters (camera height)
    
    def is_valid_position(self, position: RoomPosition) -> bool:
        """Check if position is within room boundaries."""
        return (0 <= position.x <= self.width and 
                0 <= position.y <= self.height)


class BBoxCenterEstimator:
    """
    Simple position estimator using bounding box center.
    (バウンディングボックス中心を使用したシンプルな位置推定器)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize bbox center estimator.
        (バウンディングボックス中心推定器の初期化)
        
        Args:
            room_dimensions: Room dimensions (部屋の寸法)
            frame_width: Frame width in pixels (フレーム幅)
            frame_height: Frame height in pixels (フレーム高さ)
        """
        self.room_dimensions = room_dimensions
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Simple linear mapping from image coordinates to room coordinates
        # (画像座標から部屋座標への簡単な線形マッピング)
        self.x_scale = room_dimensions.width / frame_width
        self.y_scale = room_dimensions.height / frame_height
    
    def estimate_position(self, detection: Detection) -> RoomPosition:
        """
        Estimate room position from detection bounding box center.
        (検出バウンディングボックス中心から部屋座標での位置推定)
        
        Args:
            detection: Person detection result (人物検出結果)
            
        Returns:
            RoomPosition: Estimated room position (推定された部屋座標での位置)
        """
        center_x, center_y = detection.center
        
        # Convert image coordinates to room coordinates
        # (画像座標から部屋座標に変換)
        room_x = center_x * self.x_scale
        room_y = center_y * self.y_scale
        
        return RoomPosition(
            x=room_x,
            y=room_y,
            confidence=detection.confidence * 0.7,  # Lower confidence for simple method
            timestamp=time.time()
        )


class PerspectiveMappingEstimator:
    """
    Position estimator using perspective transformation.
    (透視変換を使用した位置推定器)
    """
    
    def __init__(self, room_dimensions: RoomDimensions):
        """
        Initialize perspective mapping estimator.
        (透視変換による位置推定器の初期化)
        
        Args:
            room_dimensions: Room dimensions (部屋の寸法)
        """
        self.room_dimensions = room_dimensions
        self.transformation_matrix: Optional[np.ndarray] = None
        self.is_calibrated = False
        
        # Default corner points for 3m x 4m room (need calibration)
        # (3m x 4m部屋のデフォルト角点・要キャリブレーション)
        self.default_image_corners = np.array([
            [100, 100],    # Top-left in image
            [540, 100],    # Top-right in image
            [640, 380],    # Bottom-right in image
            [0, 380]       # Bottom-left in image
        ], dtype=np.float32)
        
        # Real-world corner points in meters
        # (実世界での角点・メートル単位)
        self.room_corners = np.array([
            [0, 0],                                    # Top-left (0, 0)
            [room_dimensions.width, 0],                # Top-right (4, 0)
            [room_dimensions.width, room_dimensions.height],  # Bottom-right (4, 3)
            [0, room_dimensions.height]                # Bottom-left (0, 3)
        ], dtype=np.float32)
    
    def calibrate(self, image_corners: np.ndarray) -> bool:
        """
        Calibrate perspective transformation using corner points.
        (角点を使用して透視変換をキャリブレーション)
        
        Args:
            image_corners: Four corner points in image coordinates (画像内の4つの角点)
            
        Returns:
            bool: Success status (成功状態)
        """
        try:
            if image_corners.shape != (4, 2):
                logger.error("Image corners must be 4x2 array")
                return False
                
            # Calculate perspective transformation matrix
            # (透視変換行列を計算)
            self.transformation_matrix = cv2.getPerspectiveTransform(
                image_corners.astype(np.float32), 
                self.room_corners
            )
            
            self.is_calibrated = True
            logger.info("Perspective mapping calibrated successfully")
            logger.info("透視変換のキャリブレーションが成功しました")
            return True
            
        except Exception as e:
            logger.error(f"Perspective calibration failed: {e}")
            logger.error(f"透視変換のキャリブレーションに失敗: {e}")
            return False
    
    def use_default_calibration(self) -> bool:
        """
        Use default calibration for testing.
        (テスト用のデフォルトキャリブレーションを使用)
        
        Returns:
            bool: Success status (成功状態)
        """
        return self.calibrate(self.default_image_corners)
    
    def estimate_position(self, detection: Detection) -> Optional[RoomPosition]:
        """
        Estimate room position using perspective transformation.
        (透視変換を使用して部屋座標での位置推定)
        
        Args:
            detection: Person detection result (人物検出結果)
            
        Returns:
            Optional[RoomPosition]: Estimated room position or None (推定された部屋座標での位置またはNone)
        """
        if not self.is_calibrated or self.transformation_matrix is None:
            logger.warning("Perspective mapping not calibrated")
            return None
        
        try:
            # Use bottom center of bounding box as foot position
            # (バウンディングボックスの底辺中心を足の位置として使用)
            x, y, w, h = detection.bbox
            foot_x = x + w // 2
            foot_y = y + h  # Bottom of bounding box
            
            # Transform image coordinates to room coordinates
            # (画像座標から部屋座標に変換)
            image_point = np.array([[[foot_x, foot_y]]], dtype=np.float32)
            room_point = cv2.perspectiveTransform(image_point, self.transformation_matrix)
            
            room_x, room_y = room_point[0][0]
            
            position = RoomPosition(
                x=float(room_x),
                y=float(room_y),
                confidence=detection.confidence * 0.9,  # High confidence for calibrated method
                timestamp=time.time()
            )
            
            # Validate position is within room boundaries
            # (位置が部屋の境界内にあることを確認)
            if not self.room_dimensions.is_valid_position(position):
                logger.warning(f"Estimated position outside room bounds: ({room_x:.2f}, {room_y:.2f})")
                position.confidence *= 0.5  # Reduce confidence for out-of-bounds positions
            
            return position
            
        except Exception as e:
            logger.error(f"Position estimation failed: {e}")
            logger.error(f"位置推定に失敗: {e}")
            return None


class DepthEstimationEstimator:
    """
    Position estimator using depth estimation from person size.
    (人物サイズからの深度推定を使用した位置推定器)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize depth estimation estimator.
        (深度推定による位置推定器の初期化)
        
        Args:
            room_dimensions: Room dimensions (部屋の寸法)
            frame_width: Frame width in pixels (フレーム幅)
            frame_height: Frame height in pixels (フレーム高さ)
        """
        self.room_dimensions = room_dimensions
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Assumed average person height in meters
        # (想定される平均的な人の身長・メートル単位)
        self.average_person_height = 1.7
        
        # Camera parameters (need calibration for accuracy)
        # (カメラパラメータ・精度にはキャリブレーションが必要)
        self.camera_focal_length = 500  # pixels (estimated)
        self.camera_height = room_dimensions.camera_height
    
    def estimate_position(self, detection: Detection) -> RoomPosition:
        """
        Estimate room position using depth estimation.
        (深度推定を使用して部屋座標での位置推定)
        
        Args:
            detection: Person detection result (人物検出結果)
            
        Returns:
            RoomPosition: Estimated room position (推定された部屋座標での位置)
        """
        x, y, w, h = detection.bbox
        
        # Estimate depth from person height in pixels
        # (ピクセル単位での人の高さから深度を推定)
        if h > 0:
            estimated_depth = (self.average_person_height * self.camera_focal_length) / h
        else:
            estimated_depth = self.room_dimensions.height / 2  # Default to room center
        
        # Convert image coordinates to room coordinates
        # (画像座標から部屋座標に変換)
        center_x, center_y = detection.center
        
        # Calculate horizontal position using similar triangles
        # (相似三角形を使用して水平位置を計算)
        room_x = ((center_x - self.frame_width / 2) * estimated_depth) / self.camera_focal_length
        room_x = room_x + self.room_dimensions.width / 2  # Adjust for room center
        
        # Depth corresponds to distance from camera (y-axis)
        # (深度はカメラからの距離に対応・y軸)
        room_y = estimated_depth
        
        # Clamp to room boundaries
        # (部屋の境界内にクランプ)
        room_x = max(0, min(room_x, self.room_dimensions.width))
        room_y = max(0, min(room_y, self.room_dimensions.height))
        
        confidence = detection.confidence * 0.8  # Moderate confidence for depth estimation
        
        return RoomPosition(
            x=room_x,
            y=room_y,
            confidence=confidence,
            timestamp=time.time()
        )


class MediaPipePoseEstimator:
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
        
        self.room_dimensions = room_dimensions
        self.frame_width = frame_width
        self.frame_height = frame_height
        
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
    
    def estimate_position(self, detection: Detection, frame: np.ndarray) -> Optional[RoomPosition]:
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


class MiDaSDepthEstimator:
    """
    Position estimator using MiDaS depth estimation.
    (MiDaS深度推定を使用した位置推定器)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize MiDaS depth estimator.
        (MiDaS深度推定器の初期化)
        
        Args:
            room_dimensions: Room dimensions (部屋の寸法)
            frame_width: Frame width in pixels (フレーム幅)
            frame_height: Frame height in pixels (フレーム高さ)
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required but not installed. Run: pip install torch torchvision")
        
        self.room_dimensions = room_dimensions
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Load MiDaS model
        try:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small", pretrained=True)
            self.model.to(self.device)
            self.model.eval()
            
            # MiDaS transforms
            self.transform = torch.hub.load("intel-isl/MiDaS", "transforms")
            self.midas_transforms = self.transform.small_transform
            
            logger.info("MiDaS model loaded successfully")
            logger.info("MiDaSモデルが正常に読み込まれました")
            
        except Exception as e:
            logger.error(f"Failed to load MiDaS model: {e}")
            logger.error(f"MiDaSモデルの読み込みに失敗: {e}")
            raise
        
        # Depth to distance calibration parameters
        self.depth_scale = 1000.0  # Scaling factor for depth values
        self.baseline_depth = 100.0  # Reference depth value
    
    def estimate_position(self, detection: Detection, frame: np.ndarray) -> Optional[RoomPosition]:
        """
        Estimate room position using MiDaS depth estimation.
        (MiDaS深度推定を使用した部屋座標での位置推定)
        
        Args:
            detection: Person detection result (人物検出結果)
            frame: Input frame for depth estimation (深度推定用の入力フレーム)
            
        Returns:
            Optional[RoomPosition]: Estimated room position or None (推定された部屋座標での位置またはNone)
        """
        try:
            # Prepare input for MiDaS
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            input_tensor = self.midas_transforms(rgb_frame).unsqueeze(0).to(self.device)
            
            # Generate depth map
            with torch.no_grad():
                depth_map = self.model(input_tensor)
                depth_map = torch.nn.functional.interpolate(
                    depth_map.unsqueeze(1),
                    size=(self.frame_height, self.frame_width),
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()
            
            # Extract depth information for person region
            x, y, w, h = detection.bbox
            
            # Use bottom center of bounding box for ground contact point
            foot_x = x + w // 2
            foot_y = y + h - 10  # Slightly above bottom to avoid floor
            
            # Clamp coordinates to frame boundaries
            foot_x = max(0, min(foot_x, self.frame_width - 1))
            foot_y = max(0, min(foot_y, self.frame_height - 1))
            
            # Get depth value at foot position
            depth_value = depth_map[foot_y, foot_x].cpu().numpy()
            
            # Convert depth to distance (meters)
            # MiDaS outputs inverse depth, so smaller values = farther
            distance = self.depth_scale / max(depth_value, 1.0)
            distance = min(distance, self.room_dimensions.height)  # Clamp to room size
            
            # Calculate horizontal position using perspective projection
            center_offset_x = foot_x - self.frame_width / 2
            room_x = (center_offset_x * distance) / 500.0  # Approximate focal length
            room_x = room_x + self.room_dimensions.width / 2  # Center in room
            
            # Distance corresponds to y-coordinate (depth in room)
            room_y = distance
            
            # Clamp to room boundaries
            room_x = max(0, min(room_x, self.room_dimensions.width))
            room_y = max(0, min(room_y, self.room_dimensions.height))
            
            # Confidence based on depth consistency
            depth_region = depth_map[y:y+h, x:x+w]
            depth_std = torch.std(depth_region).cpu().numpy()
            confidence_factor = max(0.5, 1.0 - depth_std / 100.0)
            
            confidence = detection.confidence * confidence_factor * 0.9
            
            return RoomPosition(
                x=room_x,
                y=room_y,
                confidence=confidence,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"MiDaS depth estimation failed: {e}")
            logger.error(f"MiDaS深度推定に失敗: {e}")
            return None


class DPTDepthEstimator:
    """
    Position estimator using DPT (Dense Prediction Transformer) depth estimation.
    (DPT深度推定を使用した位置推定器)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize DPT depth estimator.
        (DPT深度推定器の初期化)
        
        Args:
            room_dimensions: Room dimensions (部屋の寸法)
            frame_width: Frame width in pixels (フレーム幅)
            frame_height: Frame height in pixels (フレーム高さ)
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers is required but not installed. Run: pip install transformers")
        
        self.room_dimensions = room_dimensions
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Load DPT model using Transformers pipeline
        try:
            self.depth_estimator = pipeline(
                "depth-estimation", 
                model="Intel/dpt-large",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("DPT model loaded successfully")
            logger.info("DPTモデルが正常に読み込まれました")
            
        except Exception as e:
            logger.error(f"Failed to load DPT model: {e}")
            logger.error(f"DPTモデルの読み込みに失敗: {e}")
            raise
        
        # Depth calibration parameters
        self.max_depth = 10.0  # Maximum depth in meters
        self.min_depth = 0.5   # Minimum depth in meters
    
    def estimate_position(self, detection: Detection, frame: np.ndarray) -> Optional[RoomPosition]:
        """
        Estimate room position using DPT depth estimation.
        (DPT深度推定を使用した部屋座標での位置推定)
        
        Args:
            detection: Person detection result (人物検出結果)
            frame: Input frame for depth estimation (深度推定用の入力フレーム)
            
        Returns:
            Optional[RoomPosition]: Estimated room position or None (推定された部屋座標での位置またはNone)
        """
        try:
            # Convert frame to PIL Image
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Generate depth estimation
            depth_result = self.depth_estimator(pil_image)
            depth_map = np.array(depth_result["depth"])
            
            # Resize depth map to match frame size if needed
            if depth_map.shape != (self.frame_height, self.frame_width):
                depth_map = cv2.resize(
                    depth_map, 
                    (self.frame_width, self.frame_height), 
                    interpolation=cv2.INTER_LINEAR
                )
            
            # Extract depth information for person region
            x, y, w, h = detection.bbox
            
            # Use bottom center of bounding box for ground contact point
            foot_x = x + w // 2
            foot_y = y + h - 5  # Slightly above bottom
            
            # Clamp coordinates to frame boundaries
            foot_x = max(0, min(foot_x, self.frame_width - 1))
            foot_y = max(0, min(foot_y, self.frame_height - 1))
            
            # Get normalized depth value
            depth_value = depth_map[foot_y, foot_x]
            
            # Convert normalized depth to actual distance
            # DPT outputs normalized depth, convert to meters
            depth_normalized = depth_value / 255.0 if depth_map.dtype == np.uint8 else depth_value
            distance = self.min_depth + depth_normalized * (self.max_depth - self.min_depth)
            distance = min(distance, self.room_dimensions.height)
            
            # Calculate horizontal position
            center_offset_x = foot_x - self.frame_width / 2
            room_x = (center_offset_x * distance) / 500.0  # Approximate focal length
            room_x = room_x + self.room_dimensions.width / 2
            
            # Distance corresponds to y-coordinate
            room_y = distance
            
            # Clamp to room boundaries
            room_x = max(0, min(room_x, self.room_dimensions.width))
            room_y = max(0, min(room_y, self.room_dimensions.height))
            
            # Calculate confidence based on depth region consistency
            depth_region = depth_map[y:y+h, x:x+w]
            depth_std = np.std(depth_region)
            confidence_factor = max(0.6, 1.0 - depth_std / 50.0)
            
            confidence = detection.confidence * confidence_factor * 0.85
            
            return RoomPosition(
                x=room_x,
                y=room_y,
                confidence=confidence,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"DPT depth estimation failed: {e}")
            logger.error(f"DPT深度推定に失敗: {e}")
            return None


class PositionEstimator:
    """
    Unified position estimator supporting multiple estimation methods.
    (複数の推定手法をサポートする統合位置推定器)
    """
    
    def __init__(
        self,
        method: PositionMethod = PositionMethod.BBOX_CENTER,
        room_dimensions: Optional[RoomDimensions] = None,
        frame_width: int = 640,
        frame_height: int = 480
    ):
        """
        Initialize position estimator.
        (位置推定器の初期化)
        
        Args:
            method: Position estimation method (位置推定手法)
            room_dimensions: Room dimensions (部屋の寸法)
            frame_width: Frame width in pixels (フレーム幅)
            frame_height: Frame height in pixels (フレーム高さ)
        """
        self.method = method
        self.room_dimensions = room_dimensions or RoomDimensions()
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Initialize estimators based on method
        # (手法に基づいて推定器を初期化)
        if method == PositionMethod.BBOX_CENTER:
            self.estimator = BBoxCenterEstimator(
                self.room_dimensions, frame_width, frame_height
            )
        elif method == PositionMethod.PERSPECTIVE_MAPPING:
            self.estimator = PerspectiveMappingEstimator(self.room_dimensions)
            # Use default calibration for testing
            self.estimator.use_default_calibration()
        elif method == PositionMethod.DEPTH_ESTIMATION:
            self.estimator = DepthEstimationEstimator(
                self.room_dimensions, frame_width, frame_height
            )
        elif method == PositionMethod.MEDIAPIPE_POSE:
            self.estimator = MediaPipePoseEstimator(
                self.room_dimensions, frame_width, frame_height
            )
        elif method == PositionMethod.MIDAS_DEPTH:
            self.estimator = MiDaSDepthEstimator(
                self.room_dimensions, frame_width, frame_height
            )
        elif method == PositionMethod.DPT_DEPTH:
            self.estimator = DPTDepthEstimator(
                self.room_dimensions, frame_width, frame_height
            )
        else:
            raise ValueError(f"Unsupported position estimation method: {method}")
        
        # Store method for position estimation logic
        self.needs_frame = method in [
            PositionMethod.MEDIAPIPE_POSE, 
            PositionMethod.MIDAS_DEPTH, 
            PositionMethod.DPT_DEPTH
        ]
        
        # Initialization state
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize position estimator components.
        (位置推定器のコンポーネントを初期化)
        
        Returns:
            bool: True if initialization successful (初期化成功時True)
        """
        try:
            logger.info(f"Initializing position estimator with method: {self.method.value}")
            logger.info(f"位置推定器を初期化中、手法: {self.method.value}")
            
            # Log room dimensions
            logger.info(f"Room dimensions: {self.room_dimensions.width}m x {self.room_dimensions.height}m")
            logger.info(f"部屋の寸法: {self.room_dimensions.width}m x {self.room_dimensions.height}m")
            
            # Log frame dimensions
            logger.info(f"Frame dimensions: {self.frame_width}x{self.frame_height}")
            logger.info(f"フレーム寸法: {self.frame_width}x{self.frame_height}")
            
            # Initialize specific estimator if needed
            if hasattr(self.estimator, 'initialize'):
                if not self.estimator.initialize():
                    logger.error("Failed to initialize specific estimator")
                    logger.error("特定の推定器の初期化に失敗しました")
                    return False
            
            self.is_initialized = True
            logger.info("Position estimator initialized successfully")
            logger.info("位置推定器の初期化が完了しました")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize position estimator: {e}")
            logger.error(f"位置推定器の初期化に失敗しました: {e}")
            return False
    
    def estimate_positions(
        self, 
        detections: List[Detection], 
        frame: Optional[np.ndarray] = None
    ) -> List[RoomPosition]:
        """
        Estimate room positions for multiple detections.
        (複数の検出に対する部屋座標での位置推定)
        
        Args:
            detections: List of person detections (人物検出結果のリスト)
            frame: Input frame (required for some methods) (入力フレーム・一部手法で必要)
            
        Returns:
            List[RoomPosition]: List of estimated room positions (推定された部屋座標での位置のリスト)
        """
        if self.needs_frame and frame is None:
            logger.warning(f"Frame is required for {self.method.value} but not provided")
            return []
        
        positions = []
        
        for detection in detections:
            try:
                if self.method == PositionMethod.PERSPECTIVE_MAPPING:
                    position = self.estimator.estimate_position(detection)
                    if position:
                        positions.append(position)
                elif self.needs_frame:
                    # Methods that require frame data
                    position = self.estimator.estimate_position(detection, frame)
                    if position:
                        positions.append(position)
                else:
                    # Methods that only need detection data
                    position = self.estimator.estimate_position(detection)
                    if position:
                        positions.append(position)
            except Exception as e:
                logger.error(f"Position estimation failed for detection: {e}")
                continue
        
        return positions
    
    def visualize_positions(
        self, 
        frame: np.ndarray, 
        detections: List[Detection], 
        positions: List[RoomPosition]
    ) -> np.ndarray:
        """
        Visualize estimated positions on frame.
        (フレーム上で推定位置を可視化)
        
        Args:
            frame: Input frame (入力フレーム)
            detections: Detection results (検出結果)
            positions: Estimated positions (推定位置)
            
        Returns:
            np.ndarray: Frame with position visualizations (位置可視化付きフレーム)
        """
        output_frame = frame.copy()
        
        for detection, position in zip(detections, positions):
            # Draw position information
            x, y, w, h = detection.bbox
            
            # Position text
            position_text = f"({position.x:.1f}m, {position.y:.1f}m)"
            confidence_text = f"Conf: {position.confidence:.2f}"
            
            # Draw position text
            cv2.putText(
                output_frame, position_text, (x, y - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2
            )
            cv2.putText(
                output_frame, confidence_text, (x, y - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1
            )
            
            # Draw method indicator
            method_text = f"Method: {self.method.value}"
            cv2.putText(
                output_frame, method_text, (x, y - 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1
            )
            
            # Draw room grid overlay (optional)
            if hasattr(self, 'show_room_grid') and self.show_room_grid:
                self._draw_room_grid(output_frame)
        
        return output_frame
    
    def _draw_room_grid(self, frame: np.ndarray) -> None:
        """
        Draw room grid overlay on frame.
        (フレーム上に部屋グリッドオーバーレイを描画)
        
        Args:
            frame: Frame to draw on (描画対象フレーム)
        """
        # Draw grid lines representing room boundaries
        # (部屋の境界を表すグリッドラインを描画)
        height, width = frame.shape[:2]
        
        # Vertical lines (4m width)
        for i in range(5):  # 0m, 1m, 2m, 3m, 4m
            x = int((i * width) / 4)
            cv2.line(frame, (x, 0), (x, height), (128, 128, 128), 1)
        
        # Horizontal lines (3m depth)
        for i in range(4):  # 0m, 1m, 2m, 3m
            y = int((i * height) / 3)
            cv2.line(frame, (0, y), (width, y), (128, 128, 128), 1)
    
    def get_room_occupancy_map(self, positions: List[RoomPosition]) -> np.ndarray:
        """
        Generate room occupancy map from positions.
        (位置から部屋占有率マップを生成)
        
        Args:
            positions: List of room positions (部屋座標での位置のリスト)
            
        Returns:
            np.ndarray: Occupancy map (占有率マップ)
        """
        # Create occupancy map (10cm resolution)
        # (占有率マップを作成・10cm解像度)
        map_width = int(self.room_dimensions.width * 10)  # 40 cells for 4m
        map_height = int(self.room_dimensions.height * 10)  # 30 cells for 3m
        
        occupancy_map = np.zeros((map_height, map_width), dtype=np.float32)
        
        for position in positions:
            # Convert position to map coordinates
            map_x = int(position.x * 10)
            map_y = int(position.y * 10)
            
            # Clamp to map boundaries
            map_x = max(0, min(map_x, map_width - 1))
            map_y = max(0, min(map_y, map_height - 1))
            
            # Add confidence to occupancy map
            occupancy_map[map_y, map_x] += position.confidence
        
        return occupancy_map