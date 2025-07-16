# -*- coding: utf-8 -*-
"""
Position estimation interfaces and base classes.
(位置推定インターフェースと基底クラス)
"""

import math
import time
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import numpy as np

from ..detection.detector import Detection


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


class BasePositionEstimator(ABC):
    """
    Abstract base class for position estimators.
    (位置推定器の抽象基底クラス)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize base position estimator.
        (基底位置推定器の初期化)
        
        Args:
            room_dimensions: Room dimensions (部屋の寸法)
            frame_width: Frame width in pixels (フレーム幅)
            frame_height: Frame height in pixels (フレーム高さ)
        """
        self.room_dimensions = room_dimensions
        self.frame_width = frame_width
        self.frame_height = frame_height
    
    @abstractmethod
    def estimate_position(self, detection: Detection, frame: Optional[np.ndarray] = None) -> Optional[RoomPosition]:
        """
        Estimate room position from detection.
        (検出から部屋座標での位置推定)
        
        Args:
            detection: Person detection result (人物検出結果)
            frame: Input frame (optional for some methods) (入力フレーム・一部手法では任意)
            
        Returns:
            Optional[RoomPosition]: Estimated room position or None (推定された部屋座標での位置またはNone)
        """
        pass
    
    @property
    @abstractmethod
    def requires_frame(self) -> bool:
        """Whether this estimator requires frame data."""
        pass
    
    @property
    @abstractmethod
    def method_name(self) -> str:
        """Name of the estimation method."""
        pass


class SimplePositionEstimator(BasePositionEstimator):
    """
    Base class for simple position estimators that don't require frame data.
    (フレームデータを必要としないシンプルな位置推定器の基底クラス)
    """
    
    @property
    def requires_frame(self) -> bool:
        """Simple estimators don't require frame data."""
        return False


class FrameBasedPositionEstimator(BasePositionEstimator):
    """
    Base class for position estimators that require frame data.
    (フレームデータを必要とする位置推定器の基底クラス)
    """
    
    @property
    def requires_frame(self) -> bool:
        """Frame-based estimators require frame data."""
        return True
    
    def estimate_position(self, detection: Detection, frame: Optional[np.ndarray] = None) -> Optional[RoomPosition]:
        """
        Estimate position with frame validation.
        (フレーム検証付きの位置推定)
        """
        if frame is None:
            raise ValueError(f"{self.method_name} requires frame data but none provided")
        return self._estimate_with_frame(detection, frame)
    
    @abstractmethod
    def _estimate_with_frame(self, detection: Detection, frame: np.ndarray) -> Optional[RoomPosition]:
        """
        Internal method for frame-based position estimation.
        (フレームベース位置推定の内部メソッド)
        """
        pass