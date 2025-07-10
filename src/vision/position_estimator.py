"""
Position estimation module for 3m x 4m laboratory room.
(3m x 4mv¤gnMn¨šâ¸åüë)
"""

import math
import time
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from loguru import logger

from ..core.detector import Detection


class PositionMethod(Enum):
    """Position estimation method enumeration."""
    BBOX_CENTER = "bbox_center"
    PERSPECTIVE_MAPPING = "perspective_mapping"
    DEPTH_ESTIMATION = "depth_estimation"


@dataclass
class RoomPosition:
    """
    Position in the laboratory room coordinate system.
    (v¤§ûgnMn)
    """
    x: float  # meters from left wall (æÁK‰nÝâ)
    y: float  # meters from front wall (MÁK‰nÝâ)
    confidence: float  # position confidence (Mná<¦)
    timestamp: float
    
    def distance_to(self, other: 'RoomPosition') -> float:
        """Calculate distance to another position."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class RoomDimensions:
    """
    Laboratory room dimensions.
    (v¤nøÕ)
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
    (Ð¦óÇ£ó°ÜÃ¯¹-Ã’(W_!XjMn¨šh)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize bbox center estimator.
        (Ð¦óÇ£ó°ÜÃ¯¹-Ã¨šhn)
        
        Args:
            room_dimensions: Room dimensions (èKnøÕ)
            frame_width: Frame width in pixels (ÕìüàE)
            frame_height: Frame height in pixels (ÕìüàØU)
        """
        self.room_dimensions = room_dimensions
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Simple linear mapping from image coordinates to room coordinates
        # (;Ï§K‰èK§xnXjÚbÞÃÔó°)
        self.x_scale = room_dimensions.width / frame_width
        self.y_scale = room_dimensions.height / frame_height
    
    def estimate_position(self, detection: Detection) -> RoomPosition:
        """
        Estimate room position from detection bounding box center.
        (úÐ¦óÇ£ó°ÜÃ¯¹-ÃK‰èKMn’¨š)
        
        Args:
            detection: Person detection result (ºiúPœ)
            
        Returns:
            RoomPosition: Estimated room position (¨šèKMn)
        """
        center_x, center_y = detection.center
        
        # Convert image coordinates to room coordinates
        # (;Ï§’èK§k	Û)
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
    (–	Û’(W_Mn¨šh)
    """
    
    def __init__(self, room_dimensions: RoomDimensions):
        """
        Initialize perspective mapping estimator.
        (–	ÛMn¨šhn)
        
        Args:
            room_dimensions: Room dimensions (èKnøÕ)
        """
        self.room_dimensions = room_dimensions
        self.transformation_matrix: Optional[np.ndarray] = None
        self.is_calibrated = False
        
        # Default corner points for 3m x 4m room (need calibration)
        # (3m x 4mèKnÇÕ©ëÈ³üÊüÝ¤óÈc	)
        self.default_image_corners = np.array([
            [100, 100],    # Top-left in image
            [540, 100],    # Top-right in image
            [640, 380],    # Bottom-right in image
            [0, 380]       # Bottom-left in image
        ], dtype=np.float32)
        
        # Real-world corner points in meters
        # (ŸLn³üÊüÝ¤óÈáüÈëXM	)
        self.room_corners = np.array([
            [0, 0],                                    # Top-left (0, 0)
            [room_dimensions.width, 0],                # Top-right (4, 0)
            [room_dimensions.width, room_dimensions.height],  # Bottom-right (4, 3)
            [0, room_dimensions.height]                # Bottom-left (0, 3)
        ], dtype=np.float32)
    
    def calibrate(self, image_corners: np.ndarray) -> bool:
        """
        Calibrate perspective transformation using corner points.
        (³üÊüÝ¤óÈ’(Wf–	Û’c)
        
        Args:
            image_corners: Four corner points in image coordinates (;Ï§gn4dn³üÊüÝ¤óÈ)
            
        Returns:
            bool: Success status (Ÿ¶K)
        """
        try:
            if image_corners.shape != (4, 2):
                logger.error("Image corners must be 4x2 array")
                return False
                
            # Calculate perspective transformation matrix
            # (–	ÛL’—)
            self.transformation_matrix = cv2.getPerspectiveTransform(
                image_corners.astype(np.float32), 
                self.room_corners
            )
            
            self.is_calibrated = True
            logger.info("Perspective mapping calibrated successfully")
            logger.info("–	ÛncLŸW~W_")
            return True
            
        except Exception as e:
            logger.error(f"Perspective calibration failed: {e}")
            logger.error(f"–	Ûnck1W: {e}")
            return False
    
    def use_default_calibration(self) -> bool:
        """
        Use default calibration for testing.
        (Æ¹È(nÇÕ©ëÈc’()
        
        Returns:
            bool: Success status (Ÿ¶K)
        """
        return self.calibrate(self.default_image_corners)
    
    def estimate_position(self, detection: Detection) -> Optional[RoomPosition]:
        """
        Estimate room position using perspective transformation.
        (–	Û’(WfèKMn’¨š)
        
        Args:
            detection: Person detection result (ºiúPœ)
            
        Returns:
            Optional[RoomPosition]: Estimated room position or None (¨šèKMn~_oNone)
        """
        if not self.is_calibrated or self.transformation_matrix is None:
            logger.warning("Perspective mapping not calibrated")
            return None
        
        try:
            # Use bottom center of bounding box as foot position
            # (Ð¦óÇ£ó°ÜÃ¯¹n•º-Ã’³nMnhWf()
            x, y, w, h = detection.bbox
            foot_x = x + w // 2
            foot_y = y + h  # Bottom of bounding box
            
            # Transform image coordinates to room coordinates
            # (;Ï§’èK§k	Û)
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
            # (MnLèKnƒL…kB‹Sh’<)
            if not self.room_dimensions.is_valid_position(position):
                logger.warning(f"Estimated position outside room bounds: ({room_x:.2f}, {room_y:.2f})")
                position.confidence *= 0.5  # Reduce confidence for out-of-bounds positions
            
            return position
            
        except Exception as e:
            logger.error(f"Position estimation failed: {e}")
            logger.error(f"Mn¨šk1W: {e}")
            return None


class DepthEstimationEstimator:
    """
    Position estimator using depth estimation from person size.
    (ºiµ¤ºK‰nñ¦¨š’(W_Mn¨šh)
    """
    
    def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
        """
        Initialize depth estimation estimator.
        (ñ¦¨šMn¨šhn)
        
        Args:
            room_dimensions: Room dimensions (èKnøÕ)
            frame_width: Frame width in pixels (ÕìüàE)
            frame_height: Frame height in pixels (ÕìüàØU)
        """
        self.room_dimensions = room_dimensions
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Assumed average person height in meters
        # (sG„jºn«wáüÈëXM	)
        self.average_person_height = 1.7
        
        # Camera parameters (need calibration for accuracy)
        # («áéÑéáü¿¾¦n_kcLÅ	)
        self.camera_focal_length = 500  # pixels (estimated)
        self.camera_height = room_dimensions.camera_height
    
    def estimate_position(self, detection: Detection) -> RoomPosition:
        """
        Estimate room position using depth estimation.
        (ñ¦¨š’(WfèKMn’¨š)
        
        Args:
            detection: Person detection result (ºiúPœ)
            
        Returns:
            RoomPosition: Estimated room position (¨šèKMn)
        """
        x, y, w, h = detection.bbox
        
        # Estimate depth from person height in pixels
        # (Ô¯»ëXMgnºnØUK‰ñ¦’¨š)
        if h > 0:
            estimated_depth = (self.average_person_height * self.camera_focal_length) / h
        else:
            estimated_depth = self.room_dimensions.height / 2  # Default to room center
        
        # Convert image coordinates to room coordinates
        # (;Ï§’èK§k	Û)
        center_x, center_y = detection.center
        
        # Calculate horizontal position using similar triangles
        # (ø<	Òb’(Wf4sMn’—)
        room_x = ((center_x - self.frame_width / 2) * estimated_depth) / self.camera_focal_length
        room_x = room_x + self.room_dimensions.width / 2  # Adjust for room center
        
        # Depth corresponds to distance from camera (y-axis)
        # (ñ¦o«áéK‰nÝâkþÜyø	)
        room_y = estimated_depth
        
        # Clamp to room boundaries
        # (èKnƒLk¯éó×)
        room_x = max(0, min(room_x, self.room_dimensions.width))
        room_y = max(0, min(room_y, self.room_dimensions.height))
        
        confidence = detection.confidence * 0.8  # Moderate confidence for depth estimation
        
        return RoomPosition(
            x=room_x,
            y=room_y,
            confidence=confidence,
            timestamp=time.time()
        )


class PositionEstimator:
    """
    Unified position estimator supporting multiple estimation methods.
    (pn¨š¹Õ’µÝüÈY‹qMn¨šh)
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
        (Mn¨šhn)
        
        Args:
            method: Position estimation method (Mn¨š¹Õ)
            room_dimensions: Room dimensions (èKnøÕ)
            frame_width: Frame width in pixels (ÕìüàE)
            frame_height: Frame height in pixels (ÕìüàØU)
        """
        self.method = method
        self.room_dimensions = room_dimensions or RoomDimensions()
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Initialize estimators based on method
        # (¹ÕkúeDf¨šh’)
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
        else:
            raise ValueError(f"Unsupported position estimation method: {method}")
    
    def estimate_positions(self, detections: List[Detection]) -> List[RoomPosition]:
        """
        Estimate room positions for multiple detections.
        (pnúkþY‹èKMn’¨š)
        
        Args:
            detections: List of person detections (ºiúPœnê¹È)
            
        Returns:
            List[RoomPosition]: List of estimated room positions (¨šèKMnnê¹È)
        """
        positions = []
        
        for detection in detections:
            if self.method == PositionMethod.PERSPECTIVE_MAPPING:
                position = self.estimator.estimate_position(detection)
                if position:
                    positions.append(position)
            else:
                position = self.estimator.estimate_position(detection)
                positions.append(position)
        
        return positions
    
    def visualize_positions(
        self, 
        frame: np.ndarray, 
        detections: List[Detection], 
        positions: List[RoomPosition]
    ) -> np.ndarray:
        """
        Visualize estimated positions on frame.
        (Õìüà
k¨šMn’ï–)
        
        Args:
            frame: Input frame (e›Õìüà)
            detections: Detection results (úPœ)
            positions: Estimated positions (¨šMn)
            
        Returns:
            np.ndarray: Frame with position visualizations (Mnï–Õìüà)
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
            
            # Draw room grid overlay (optional)
            if hasattr(self, 'show_room_grid') and self.show_room_grid:
                self._draw_room_grid(output_frame)
        
        return output_frame
    
    def _draw_room_grid(self, frame: np.ndarray) -> None:
        """
        Draw room grid overlay on frame.
        (Õìüà
kèK°êÃÉªüÐüì¤’Ï;)
        
        Args:
            frame: Frame to draw on (Ï;þaÕìüà)
        """
        # Draw grid lines representing room boundaries
        # (èKnƒL’hY°êÃÉÚ’Ï;)
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
        (MnK‰èK`	ÞÃ×’)
        
        Args:
            positions: List of room positions (èKMnnê¹È)
            
        Returns:
            np.ndarray: Occupancy map (`	ÞÃ×)
        """
        # Create occupancy map (10cm resolution)
        # (`	ÞÃ×’\10cmãÏ¦	)
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