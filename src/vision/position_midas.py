# -*- coding: utf-8 -*-
"""
MiDaS depth estimation based position estimation.
(MiDaS深度推定ベースの位置推定)
"""

import time
from typing import Optional

import cv2
import numpy as np
from loguru import logger

from ..core.detector import Detection
from ..core.position_interface import FrameBasedPositionEstimator, RoomPosition, RoomDimensions

# Optional imports for PyTorch and MiDaS
try:
    import torch
    import torchvision.transforms as transforms
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Install with: pip install torch torchvision")


class MiDaSDepthEstimator(FrameBasedPositionEstimator):
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
        
        super().__init__(room_dimensions, frame_width, frame_height)
        
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
    
    @property
    def method_name(self) -> str:
        """Name of the estimation method."""
        return "midas_depth"
    
    def _estimate_with_frame(self, detection: Detection, frame: np.ndarray) -> Optional[RoomPosition]:
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