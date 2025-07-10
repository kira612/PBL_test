# -*- coding: utf-8 -*-
"""
DPT (Dense Prediction Transformer) depth estimation based position estimation.
(DPT深度推定ベースの位置推定)
"""

import time
from typing import Optional

import cv2
import numpy as np
from loguru import logger

from ..core.detector import Detection
from ..core.position_interface import FrameBasedPositionEstimator, RoomPosition, RoomDimensions

# Optional imports for Transformers and PyTorch
try:
    import torch
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


class DPTDepthEstimator(FrameBasedPositionEstimator):
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
        
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required but not installed. Run: pip install torch torchvision")
        
        super().__init__(room_dimensions, frame_width, frame_height)
        
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
    
    @property
    def method_name(self) -> str:
        """Name of the estimation method."""
        return "dpt_depth"
    
    def _estimate_with_frame(self, detection: Detection, frame: np.ndarray) -> Optional[RoomPosition]:
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