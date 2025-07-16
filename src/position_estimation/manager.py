# -*- coding: utf-8 -*-
"""
Unified position estimation manager supporting multiple methods.
(複数の手法をサポートする統合位置推定管理器)
"""

import time
from typing import List, Optional, Dict, Any

import cv2
import numpy as np
from loguru import logger

from ..detection.detector import Detection
from .interface import (
    PositionMethod, 
    RoomPosition, 
    RoomDimensions, 
    BasePositionEstimator
)

# Import position estimators
from .perspective.perspective import (
    BBoxCenterEstimator,
    PerspectiveMappingEstimator,
    DepthEstimationEstimator
)
from .ai_models.mediapipe import MediaPipePoseEstimator
from .ai_models.midas import MiDaSDepthEstimator
from .ai_models.dpt import DPTDepthEstimator


class PositionEstimationManager:
    """
    Unified position estimation manager supporting multiple estimation methods.
    (複数の推定手法をサポートする統合位置推定管理器)
    """
    
    def __init__(
        self,
        method: PositionMethod = PositionMethod.BBOX_CENTER,
        room_dimensions: Optional[RoomDimensions] = None,
        frame_width: int = 640,
        frame_height: int = 480
    ):
        """
        Initialize position estimation manager.
        (位置推定管理器の初期化)
        
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
        
        # Initialize estimator based on method
        self.estimator = self._create_estimator(method)
        
        # Track estimation statistics
        self.estimation_stats = {
            'total_estimations': 0,
            'successful_estimations': 0,
            'failed_estimations': 0,
            'average_confidence': 0.0
        }
    
    def _create_estimator(self, method: PositionMethod) -> BasePositionEstimator:
        """
        Create position estimator based on method.
        (手法に基づいて位置推定器を作成)
        
        Args:
            method: Position estimation method (位置推定手法)
            
        Returns:
            BasePositionEstimator: Position estimator instance (位置推定器インスタンス)
        """
        try:
            if method == PositionMethod.BBOX_CENTER:
                return BBoxCenterEstimator(
                    self.room_dimensions, self.frame_width, self.frame_height
                )
            elif method == PositionMethod.PERSPECTIVE_MAPPING:
                estimator = PerspectiveMappingEstimator(
                    self.room_dimensions, self.frame_width, self.frame_height
                )
                # Use default calibration for testing
                estimator.use_default_calibration()
                return estimator
            elif method == PositionMethod.DEPTH_ESTIMATION:
                return DepthEstimationEstimator(
                    self.room_dimensions, self.frame_width, self.frame_height
                )
            elif method == PositionMethod.MEDIAPIPE_POSE:
                return MediaPipePoseEstimator(
                    self.room_dimensions, self.frame_width, self.frame_height
                )
            elif method == PositionMethod.MIDAS_DEPTH:
                return MiDaSDepthEstimator(
                    self.room_dimensions, self.frame_width, self.frame_height
                )
            elif method == PositionMethod.DPT_DEPTH:
                return DPTDepthEstimator(
                    self.room_dimensions, self.frame_width, self.frame_height
                )
            else:
                raise ValueError(f"Unsupported position estimation method: {method}")
                
        except Exception as e:
            logger.error(f"Failed to create estimator for {method.value}: {e}")
            logger.warning(f"Falling back to BBoxCenterEstimator")
            return BBoxCenterEstimator(
                self.room_dimensions, self.frame_width, self.frame_height
            )
    
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
        if self.estimator.requires_frame and frame is None:
            logger.warning(f"Frame is required for {self.method.value} but not provided")
            return []
        
        positions = []
        confidences = []
        
        for detection in detections:
            try:
                self.estimation_stats['total_estimations'] += 1
                
                # Estimate position
                position = self.estimator.estimate_position(detection, frame)
                
                if position:
                    positions.append(position)
                    confidences.append(position.confidence)
                    self.estimation_stats['successful_estimations'] += 1
                else:
                    self.estimation_stats['failed_estimations'] += 1
                    
            except Exception as e:
                logger.error(f"Position estimation failed for detection: {e}")
                self.estimation_stats['failed_estimations'] += 1
                continue
        
        # Update average confidence
        if confidences:
            self.estimation_stats['average_confidence'] = sum(confidences) / len(confidences)
        
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
            # Draw bounding box
            x, y, w, h = detection.bbox
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Position text
            position_text = f"({position.x:.1f}m, {position.y:.1f}m)"
            confidence_text = f"Conf: {position.confidence:.2f}"
            method_text = f"Method: {self.method.value}"
            
            # Draw position information
            cv2.putText(
                output_frame, position_text, (x, y - 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2
            )
            cv2.putText(
                output_frame, confidence_text, (x, y - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1
            )
            cv2.putText(
                output_frame, method_text, (x, y - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1
            )
        
        # Draw method info and statistics
        self._draw_info_overlay(output_frame)
        
        return output_frame
    
    def _draw_info_overlay(self, frame: np.ndarray) -> None:
        """
        Draw information overlay on frame.
        (フレームに情報オーバーレイを描画)
        
        Args:
            frame: Frame to draw on (描画対象フレーム)
        """
        # Method information
        method_info = f"Position Method: {self.method.value}"
        cv2.putText(
            frame, method_info, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )
        
        # Statistics
        stats = self.estimation_stats
        success_rate = 0.0
        if stats['total_estimations'] > 0:
            success_rate = stats['successful_estimations'] / stats['total_estimations']
        
        stats_text = f"Success: {success_rate:.1%} | Avg Conf: {stats['average_confidence']:.2f}"
        cv2.putText(
            frame, stats_text, (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
        )
    
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
    
    def change_method(self, new_method: PositionMethod) -> bool:
        """
        Change position estimation method.
        (位置推定手法を変更)
        
        Args:
            new_method: New position estimation method (新しい位置推定手法)
            
        Returns:
            bool: Success status (成功状態)
        """
        try:
            old_method = self.method
            self.method = new_method
            self.estimator = self._create_estimator(new_method)
            
            # Reset statistics
            self.estimation_stats = {
                'total_estimations': 0,
                'successful_estimations': 0,
                'failed_estimations': 0,
                'average_confidence': 0.0
            }
            
            logger.info(f"Position estimation method changed from {old_method.value} to {new_method.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to change method to {new_method.value}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get estimation statistics.
        (推定統計情報を取得)
        
        Returns:
            Dict[str, Any]: Statistics dictionary (統計情報辞書)
        """
        return {
            'method': self.method.value,
            'requires_frame': self.estimator.requires_frame,
            'room_dimensions': {
                'width': self.room_dimensions.width,
                'height': self.room_dimensions.height,
                'camera_height': self.room_dimensions.camera_height
            },
            'frame_size': {
                'width': self.frame_width,
                'height': self.frame_height
            },
            'estimation_stats': self.estimation_stats.copy()
        }
    
    @property
    def requires_frame(self) -> bool:
        """Whether this manager's current estimator requires frame data."""
        return self.estimator.requires_frame
    
    @property
    def current_method(self) -> PositionMethod:
        """Current position estimation method."""
        return self.method