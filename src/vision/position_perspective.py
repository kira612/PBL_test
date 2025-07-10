# -*- coding: utf-8 -*-
"""
Perspective transformation based position estimation.
(透視変換ベースの位置推定)
"""

import time
from typing import Optional

import cv2
import numpy as np
from loguru import logger

from ..core.detector import Detection
from ..core.position_interface import SimplePositionEstimator, RoomPosition, RoomDimensions


class BBoxCenterEstimator(SimplePositionEstimator):
    """
    Simple position estimator using bounding box center.
    (バウンディングボックス中心を使用したシンプルな位置推定器)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize bbox center estimator.
        (バウンディングボックス中心推定器の初期化)
        """
        super().__init__(room_dimensions, frame_width, frame_height)
        
        # Simple linear mapping from image coordinates to room coordinates
        # (画像座標から部屋座標への簡単な線形マッピング)
        self.x_scale = room_dimensions.width / frame_width
        self.y_scale = room_dimensions.height / frame_height
    
    @property
    def method_name(self) -> str:
        """Name of the estimation method."""
        return "bbox_center"
    
    def estimate_position(self, detection: Detection, frame: Optional[np.ndarray] = None) -> Optional[RoomPosition]:
        """
        Estimate room position from detection bounding box center.
        (検出バウンディングボックス中心から部屋座標での位置推定)
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


class PerspectiveMappingEstimator(SimplePositionEstimator):
    """
    Position estimator using perspective transformation.
    (透視変換を使用した位置推定器)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int = 640, frame_height: int = 480):
        """
        Initialize perspective mapping estimator.
        (透視変換による位置推定器の初期化)
        """
        super().__init__(room_dimensions, frame_width, frame_height)
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
    
    @property
    def method_name(self) -> str:
        """Name of the estimation method."""
        return "perspective_mapping"
    
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
    
    def estimate_position(self, detection: Detection, frame: Optional[np.ndarray] = None) -> Optional[RoomPosition]:
        """
        Estimate room position using perspective transformation.
        (透視変換を使用して部屋座標での位置推定)
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


class DepthEstimationEstimator(SimplePositionEstimator):
    """
    Position estimator using depth estimation from person size.
    (人物サイズからの深度推定を使用した位置推定器)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize depth estimation estimator.
        (深度推定による位置推定器の初期化)
        """
        super().__init__(room_dimensions, frame_width, frame_height)
        
        # Assumed average person height in meters
        # (想定される平均的な人の身長・メートル単位)
        self.average_person_height = 1.7
        
        # Camera parameters (need calibration for accuracy)
        # (カメラパラメータ・精度にはキャリブレーションが必要)
        self.camera_focal_length = 500  # pixels (estimated)
        self.camera_height = room_dimensions.camera_height
    
    @property
    def method_name(self) -> str:
        """Name of the estimation method."""
        return "depth_estimation"
    
    def estimate_position(self, detection: Detection, frame: Optional[np.ndarray] = None) -> Optional[RoomPosition]:
        """
        Estimate room position using depth estimation.
        (深度推定を使用して部屋座標での位置推定)
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