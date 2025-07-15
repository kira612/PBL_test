"""
Visualization module for displaying monitoring results with overlays.
(監視結果をオーバーレイ表示するための可視化モジュール)
"""

import time
import math
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from loguru import logger

from ..core.detector import Detection
from ..vision.position_estimator import RoomPosition
from ..vision.action_recognizer import ActionResult, ActionType


class DisplayMode(Enum):
    """Display mode enumeration."""
    NONE = "none"
    WINDOW = "window"
    HEADLESS = "headless"


@dataclass
class DisplayConfig:
    """
    Configuration for display visualization.
    (表示可視化の設定)
    """
    mode: DisplayMode = DisplayMode.NONE
    window_name: str = "Laboratory Monitoring System"
    window_width: int = 1280
    window_height: int = 720
    show_fps: bool = True
    show_detection_count: bool = True
    show_position_info: bool = True
    show_action_info: bool = True
    bbox_thickness: int = 2
    text_scale: float = 0.6
    text_thickness: int = 2


class MonitoringDisplay:
    """
    Display manager for monitoring system visualization.
    (監視システム可視化のディスプレイマネージャー)
    """
    
    def __init__(self, config: DisplayConfig):
        """
        Initialize monitoring display.
        (監視ディスプレイの初期化)
        
        Args:
            config: Display configuration (表示設定)
        """
        self.config = config
        self.is_initialized = False
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0
        
        # Color definitions (BGR format for OpenCV)
        self.colors = {
            'person': (0, 255, 0),      # Green for person detection
            'bbox': (0, 255, 0),        # Green for bounding box
            'text': (255, 255, 255),    # White for text
            'background': (0, 0, 0),    # Black for text background
            'position': (255, 0, 0),    # Blue for position markers
            'action_standing': (0, 255, 255),     # Yellow for standing
            'action_sitting': (0, 165, 255),     # Orange for sitting
            'action_computer': (255, 0, 255),    # Magenta for computer interaction
            'action_walking': (255, 255, 0),     # Cyan for walking
            'action_unknown': (128, 128, 128),   # Gray for unknown
        }
        
        # Action type to color mapping
        self.action_colors = {
            ActionType.STANDING: self.colors['action_standing'],
            ActionType.SITTING: self.colors['action_sitting'],
            ActionType.COMPUTER_INTERACTION: self.colors['action_computer'],
            ActionType.WALKING: self.colors['action_walking'],
            ActionType.UNKNOWN: self.colors['action_unknown'],
        }
        
    def initialize(self) -> bool:
        """
        Initialize display system.
        (表示システムの初期化)
        
        Returns:
            bool: True if initialization successful (初期化成功時True)
        """
        try:
            if self.config.mode == DisplayMode.WINDOW:
                # Create window for visualization
                cv2.namedWindow(self.config.window_name, cv2.WINDOW_RESIZABLE)
                cv2.resizeWindow(self.config.window_name, 
                               self.config.window_width, 
                               self.config.window_height)
                
                logger.info(f"Display window initialized: {self.config.window_name}")
                logger.info(f"表示ウィンドウが初期化されました: {self.config.window_name}")
            
            elif self.config.mode == DisplayMode.HEADLESS:
                logger.info("Headless display mode initialized")
                logger.info("ヘッドレス表示モードが初期化されました")
            
            else:
                logger.info("Display disabled")
                logger.info("表示が無効になっています")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            logger.error(f"表示の初期化に失敗しました: {e}")
            return False
    
    def update_fps(self) -> None:
        """
        Update FPS counter.
        (FPSカウンターの更新)
        """
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def draw_detection_box(self, 
                          image: np.ndarray, 
                          detection: Detection,
                          position: Optional[RoomPosition] = None,
                          action: Optional[ActionResult] = None) -> None:
        """
        Draw detection bounding box with labels.
        (検出バウンディングボックスとラベルの描画)
        
        Args:
            image: Input image (入力画像)
            detection: Detection result (検出結果)
            position: Room position (部屋での位置)
            action: Action result (行動結果)
        """
        x, y, w, h = detection.bbox
        
        # Draw bounding box
        cv2.rectangle(image, (x, y), (x + w, y + h), 
                     self.colors['bbox'], self.config.bbox_thickness)
        
        # Prepare label text
        labels = []
        
        # Add object category (assuming person detection)
        labels.append(f"Person: {detection.confidence:.2f}")
        
        # Add position information
        if position and self.config.show_position_info:
            distance = math.sqrt(position.x**2 + position.y**2)
            labels.append(f"Pos: ({position.x:.1f}, {position.y:.1f})m")
            labels.append(f"Dist: {distance:.1f}m")
        
        # Add action information
        if action and self.config.show_action_info:
            action_name = action.action_type.value
            labels.append(f"Action: {action_name}")
            labels.append(f"Conf: {action.confidence:.2f}")
        
        # Draw labels
        label_y = y - 10
        for i, label in enumerate(labels):
            # Calculate text size
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 
                self.config.text_scale, self.config.text_thickness
            )
            
            # Draw text background
            cv2.rectangle(image, 
                         (x, label_y - text_height - baseline), 
                         (x + text_width, label_y + baseline),
                         self.colors['background'], -1)
            
            # Draw text
            cv2.putText(image, label, (x, label_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, self.config.text_scale, 
                       self.colors['text'], self.config.text_thickness)
            
            label_y -= (text_height + baseline + 5)
        
        # Draw center point
        center_x = x + w // 2
        center_y = y + h // 2
        cv2.circle(image, (center_x, center_y), 3, self.colors['position'], -1)
        
        # Color-code bounding box based on action if available
        if action:
            action_color = self.action_colors.get(action.action_type, self.colors['bbox'])
            cv2.rectangle(image, (x, y), (x + w, y + h), action_color, 2)
    
    def draw_system_info(self, image: np.ndarray, 
                        detection_count: int = 0,
                        additional_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Draw system information overlay.
        (システム情報オーバーレイの描画)
        
        Args:
            image: Input image (入力画像)
            detection_count: Number of detections (検出数)
            additional_info: Additional information to display (追加表示情報)
        """
        info_lines = []
        
        # Add FPS information
        if self.config.show_fps:
            info_lines.append(f"FPS: {self.current_fps:.1f}")
        
        # Add detection count
        if self.config.show_detection_count:
            info_lines.append(f"Detections: {detection_count}")
        
        # Add timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        info_lines.append(f"Time: {timestamp}")
        
        # Add additional information
        if additional_info:
            for key, value in additional_info.items():
                info_lines.append(f"{key}: {value}")
        
        # Draw information in top-left corner
        y_offset = 30
        for line in info_lines:
            # Calculate text size
            (text_width, text_height), baseline = cv2.getTextSize(
                line, cv2.FONT_HERSHEY_SIMPLEX, 
                self.config.text_scale, self.config.text_thickness
            )
            
            # Draw text background
            cv2.rectangle(image, 
                         (10, y_offset - text_height - baseline), 
                         (10 + text_width, y_offset + baseline),
                         self.colors['background'], -1)
            
            # Draw text
            cv2.putText(image, line, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, self.config.text_scale, 
                       self.colors['text'], self.config.text_thickness)
            
            y_offset += text_height + baseline + 10
    
    def draw_room_layout(self, image: np.ndarray, 
                        room_width: float, room_height: float,
                        positions: List[RoomPosition]) -> None:
        """
        Draw room layout with position markers.
        (部屋レイアウトと位置マーカーの描画)
        
        Args:
            image: Input image (入力画像)
            room_width: Room width in meters (部屋の幅)
            room_height: Room height in meters (部屋の高さ)
            positions: List of room positions (部屋座標での位置リスト)
        """
        # Draw room layout in bottom-right corner
        layout_width = 200
        layout_height = 150
        layout_x = image.shape[1] - layout_width - 20
        layout_y = image.shape[0] - layout_height - 20
        
        # Draw room boundary
        cv2.rectangle(image, (layout_x, layout_y), 
                     (layout_x + layout_width, layout_y + layout_height),
                     self.colors['text'], 2)
        
        # Draw room dimensions
        cv2.putText(image, f"{room_width}m x {room_height}m", 
                   (layout_x, layout_y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                   self.colors['text'], 1)
        
        # Draw position markers
        for position in positions:
            # Convert room coordinates to layout coordinates
            marker_x = int(layout_x + (position.x / room_width) * layout_width)
            marker_y = int(layout_y + (position.y / room_height) * layout_height)
            
            # Draw position marker
            cv2.circle(image, (marker_x, marker_y), 5, self.colors['position'], -1)
            
            # Draw confidence indicator
            confidence_radius = int(10 * position.confidence)
            cv2.circle(image, (marker_x, marker_y), confidence_radius, 
                      self.colors['position'], 1)
    
    def render_frame(self, 
                    frame: np.ndarray,
                    detections: List[Detection],
                    positions: List[RoomPosition],
                    actions: List[ActionResult],
                    room_width: float = 4.0,
                    room_height: float = 3.0,
                    additional_info: Optional[Dict[str, Any]] = None) -> Optional[np.ndarray]:
        """
        Render frame with all visualization overlays.
        (全ての可視化オーバーレイでフレームをレンダリング)
        
        Args:
            frame: Input frame (入力フレーム)
            detections: List of detections (検出リスト)
            positions: List of positions (位置リスト)
            actions: List of actions (行動リスト)
            room_width: Room width in meters (部屋の幅)
            room_height: Room height in meters (部屋の高さ)
            additional_info: Additional information (追加情報)
            
        Returns:
            Optional[np.ndarray]: Rendered frame or None (レンダリング済みフレームまたはNone)
        """
        if self.config.mode == DisplayMode.NONE:
            return None
        
        # Update FPS counter
        self.update_fps()
        
        # Create copy of frame for rendering
        display_frame = frame.copy()
        
        # Draw detections with associated information
        for i, detection in enumerate(detections):
            position = positions[i] if i < len(positions) else None
            action = actions[i] if i < len(actions) else None
            
            self.draw_detection_box(display_frame, detection, position, action)
        
        # Draw system information
        self.draw_system_info(display_frame, len(detections), additional_info)
        
        # Draw room layout
        self.draw_room_layout(display_frame, room_width, room_height, positions)
        
        # Display frame if in window mode
        if self.config.mode == DisplayMode.WINDOW:
            cv2.imshow(self.config.window_name, display_frame)
            
            # Check for key press (ESC to exit)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                return None
        
        return display_frame
    
    def cleanup(self) -> None:
        """
        Clean up display resources.
        (表示リソースのクリーンアップ)
        """
        try:
            if self.config.mode == DisplayMode.WINDOW:
                cv2.destroyWindow(self.config.window_name)
                logger.info("Display window closed")
                logger.info("表示ウィンドウが閉じられました")
        
        except Exception as e:
            logger.error(f"Error during display cleanup: {e}")
            logger.error(f"表示クリーンアップ中にエラー: {e}")
    
    def is_window_open(self) -> bool:
        """
        Check if display window is still open.
        (表示ウィンドウが開いているかチェック)
        
        Returns:
            bool: True if window is open (ウィンドウが開いている場合True)
        """
        if self.config.mode != DisplayMode.WINDOW:
            return True
        
        try:
            # Check if window exists
            return cv2.getWindowProperty(self.config.window_name, cv2.WND_PROP_VISIBLE) >= 0
        except:
            return False


def create_display_config(
    mode: str = "none",
    window_name: str = "Laboratory Monitoring System",
    show_fps: bool = True,
    show_detection_count: bool = True,
    show_position_info: bool = True,
    show_action_info: bool = True
) -> DisplayConfig:
    """
    Create display configuration.
    (表示設定の作成)
    
    Args:
        mode: Display mode ("none", "window", "headless")
        window_name: Window name (ウィンドウ名)
        show_fps: Show FPS counter (FPSカウンター表示)
        show_detection_count: Show detection count (検出数表示)
        show_position_info: Show position information (位置情報表示)
        show_action_info: Show action information (行動情報表示)
        
    Returns:
        DisplayConfig: Display configuration (表示設定)
    """
    display_mode = DisplayMode.NONE
    if mode.lower() == "window":
        display_mode = DisplayMode.WINDOW
    elif mode.lower() == "headless":
        display_mode = DisplayMode.HEADLESS
    
    return DisplayConfig(
        mode=display_mode,
        window_name=window_name,
        show_fps=show_fps,
        show_detection_count=show_detection_count,
        show_position_info=show_position_info,
        show_action_info=show_action_info
    )