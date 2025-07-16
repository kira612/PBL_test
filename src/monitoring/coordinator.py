"""
System coordinator for integrating all monitoring components.
(すべての監視コンポーネントを統合するシステムコーディネーター)
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

import cv2
import numpy as np
from loguru import logger

from ..camera.manager import CameraManager
from ..detection.detector import PersonDetector, DetectionMethod
from ..position_estimation.estimator import PositionEstimator, PositionMethod, RoomDimensions
from ..action_recognition.recognizer import ActionRecognizer
from .display.display import MonitoringDisplay, DisplayConfig, create_display_config
from ..config.config import Config


class MonitoringCoordinator:
    """
    Main coordinator for the monitoring system.
    (監視システムのメインコーディネーター)
    """
    
    def __init__(
        self,
        camera_id: int = 0,
        config_path: Optional[Path] = None,
        detection_method: DetectionMethod = DetectionMethod.YOLO,
        position_method: PositionMethod = PositionMethod.BBOX_CENTER,
        display_config: Optional[DisplayConfig] = None
    ):
        """
        Initialize monitoring coordinator.
        (監視コーディネーターの初期化)
        
        Args:
            camera_id: Camera device ID (カメラデバイスID)
            config_path: Configuration file path (設定ファイルのパス)
            detection_method: Person detection method (人物検出手法)
            position_method: Position estimation method (位置推定手法)
            display_config: Display configuration (表示設定)
        """
        self.camera_id = camera_id
        self.config_path = config_path
        self.detection_method = detection_method
        self.position_method = position_method
        self.display_config = display_config or create_display_config()
        
        # Initialize components (コンポーネントの初期化)
        self.config: Optional[Config] = None
        self.camera: Optional[CameraManager] = None
        self.detector: Optional[PersonDetector] = None
        self.position_estimator: Optional[PositionEstimator] = None
        self.action_recognizer: Optional[ActionRecognizer] = None
        self.display: Optional[MonitoringDisplay] = None
        
        # Monitoring state (監視状態)
        self.is_running = False
        self.stats = {
            "total_frames": 0,
            "total_detections": 0,
            "start_time": 0.0,
            "current_fps": 0.0
        }

    async def initialize(self) -> bool:
        """
        Initialize all system components.
        (すべてのシステムコンポーネントを初期化)
        
        Returns:
            bool: Success status (成功状態)
        """
        try:
            logger.info("Initializing monitoring system components")
            logger.info("監視システムコンポーネントを初期化中")
            
            # Load configuration (設定の読み込み)
            if self.config_path:
                self.config = Config.from_file(self.config_path)
            else:
                self.config = Config.default()
            
            # Initialize camera (カメラの初期化)
            camera_config = self.config.camera
            self.camera = CameraManager(
                camera_id=self.camera_id,
                width=camera_config.width,
                height=camera_config.height,
                fps=camera_config.fps
            )
            
            if not self.camera.initialize():
                logger.error("Failed to initialize camera")
                logger.error("カメラの初期化に失敗しました")
                return False
            
            # Initialize person detector (人物検出器の初期化)
            detector_config = self.config.detection
            self.detector = PersonDetector(
                method=self.detection_method,
                confidence_threshold=detector_config.confidence_threshold,
                model_path=detector_config.yolo_model_path
            )
            
            if not self.detector.initialize():
                logger.error("Failed to initialize person detector")
                logger.error("人物検出器の初期化に失敗しました")
                return False
            
            # Initialize position estimator (位置推定器の初期化)
            position_config = self.config.position
            room_config = self.config.room
            room_dims = RoomDimensions(
                width=room_config.width,
                height=room_config.height
            )
            
            self.position_estimator = PositionEstimator(
                method=self.position_method,
                room_dimensions=room_dims,
                frame_width=camera_config.width,
                frame_height=camera_config.height
            )
            
            if not self.position_estimator.initialize():
                logger.error("Failed to initialize position estimator")
                logger.error("位置推定器の初期化に失敗しました")
                return False
            
            # Initialize action recognizer (行動認識器の初期化)
            action_config = self.config.action
            self.action_recognizer = ActionRecognizer(use_pose=action_config.use_pose)
            
            if not self.action_recognizer.initialize():
                logger.error("Failed to initialize action recognizer")
                logger.error("行動認識器の初期化に失敗しました")
                return False
            
            # Initialize display (表示の初期化)
            self.display = MonitoringDisplay(self.display_config)
            if not self.display.initialize():
                logger.error("Failed to initialize display")
                logger.error("表示の初期化に失敗しました")
                return False
            
            logger.info("All components initialized successfully")
            logger.info("すべてのコンポーネントの初期化が完了しました")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            logger.error(f"システム初期化に失敗しました: {e}")
            return False

    async def start_monitoring(self) -> None:
        """
        Start the main monitoring loop.
        (メイン監視ループを開始)
        """
        if not all([self.camera, self.detector, self.position_estimator, self.action_recognizer]):
            logger.error("Components not initialized. Call initialize() first.")
            logger.error("コンポーネントが初期化されていません。最初にinitialize()を呼び出してください。")
            return
        
        self.is_running = True
        self.stats["start_time"] = time.time()
        
        logger.info("Starting monitoring loop")
        logger.info("監視ループを開始します")
        
        try:
            frame_times = []
            
            async for frame in self.camera.get_async_frame_generator():
                if not self.is_running:
                    break
                
                start_time = time.time()
                
                # Process frame (フレーム処理)
                await self._process_frame(frame)
                
                # Update statistics (統計の更新)
                self.stats["total_frames"] += 1
                frame_time = time.time() - start_time
                frame_times.append(frame_time)
                
                # Calculate current FPS (現在のFPSを計算)
                if len(frame_times) > 30:
                    frame_times = frame_times[-30:]
                
                avg_frame_time = sum(frame_times) / len(frame_times)
                self.stats["current_fps"] = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
                
                # Log progress periodically (定期的に進捗をログ出力)
                if self.stats["total_frames"] % 100 == 0:
                    logger.info(f"Processed {self.stats['total_frames']} frames, "
                              f"FPS: {self.stats['current_fps']:.1f}, "
                              f"Detections: {self.stats['total_detections']}")
                    logger.info(f"{self.stats['total_frames']} フレーム処理完了、"
                              f"FPS: {self.stats['current_fps']:.1f}、"
                              f"検出: {self.stats['total_detections']}")
                
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
            logger.error(f"監視ループエラー: {e}")
        finally:
            logger.info("Monitoring loop stopped")
            logger.info("監視ループが停止しました")

    async def _process_frame(self, frame: np.ndarray) -> None:
        """
        Process a single frame through the entire pipeline.
        (単一フレームを全体のパイプラインで処理)
        
        Args:
            frame: Input frame (入力フレーム)
        """
        try:
            # Person detection (人物検出)
            detections = self.detector.detect_persons(frame)
            self.stats["total_detections"] += len(detections)
            
            if not detections:
                return
            
            # Position estimation for all detections (全検出の位置推定)
            try:
                positions = self.position_estimator.estimate_positions(detections, frame)
            except Exception as e:
                logger.warning(f"Position estimation failed: {e}")
                logger.warning(f"位置推定に失敗しました: {e}")
                # Create default positions if estimation fails
                positions = []
                for detection in detections:
                    x, y, w, h = detection.bbox
                    center_x = x + w / 2
                    center_y = y + h / 2
                    from ..position_estimation.estimator import RoomPosition
                    default_position = RoomPosition(
                        x=center_x / frame.shape[1] * self.config.room.width,
                        y=center_y / frame.shape[0] * self.config.room.height,
                        confidence=0.5,
                        timestamp=time.time()
                    )
                    positions.append(default_position)
            
            # Action recognition for all detections (全検出の行動認識)
            try:
                actions = self.action_recognizer.recognize_actions(detections, None, frame.shape[:2])
            except Exception as e:
                logger.warning(f"Action recognition failed: {e}")
                logger.warning(f"行動認識に失敗しました: {e}")
                # Create default actions if recognition fails
                from ..action_recognition.recognizer import ActionResult, ActionType
                actions = []
                for detection in detections:
                    default_action = ActionResult(
                        action_type=ActionType.UNKNOWN,
                        confidence=0.0,
                        timestamp=time.time()
                    )
                    actions.append(default_action)
            
            # Render frame with visualization if display is enabled
            if self.display:
                rendered_frame = self.display.render_frame(
                    frame=frame,
                    detections=detections,
                    positions=positions,
                    actions=actions,
                    room_width=self.config.room.width,
                    room_height=self.config.room.height,
                    additional_info={
                        "Total Frames": self.stats["total_frames"],
                        "Total Detections": self.stats["total_detections"]
                    }
                )
                
                # Check if window is still open (for window mode)
                if not self.display.is_window_open():
                    self.is_running = False
                    logger.info("Display window closed, stopping monitoring")
                    logger.info("表示ウィンドウが閉じられました。監視を停止します")
            
            # Log results (結果をログ出力)
            for i, detection in enumerate(detections):
                position = positions[i] if i < len(positions) else None
                action = actions[i] if i < len(actions) else None
                logger.debug(f"Detection: confidence={detection.confidence:.2f}, "
                           f"position={position}, action={action}")
                logger.debug(f"検出: 信頼度={detection.confidence:.2f}, "
                           f"位置={position}, 行動={action}")
                
        except Exception as e:
            logger.warning(f"Frame processing error: {e}")
            logger.warning(f"フレーム処理エラー: {e}")

    async def stop_monitoring(self) -> None:
        """
        Stop the monitoring system.
        (監視システムを停止)
        """
        logger.info("Stopping monitoring system")
        logger.info("監視システムを停止中")
        
        self.is_running = False
        
        # Stop all components (すべてのコンポーネントを停止)
        if self.camera:
            self.camera.stop()
        
        # Clean up display resources (表示リソースのクリーンアップ)
        if self.display:
            self.display.cleanup()
        
        # Calculate final statistics (最終統計を計算)
        total_time = time.time() - self.stats["start_time"]
        avg_fps = self.stats["total_frames"] / total_time if total_time > 0 else 0
        
        logger.info(f"Monitoring session completed:")
        logger.info(f"  Total frames: {self.stats['total_frames']}")
        logger.info(f"  Total detections: {self.stats['total_detections']}")
        logger.info(f"  Average FPS: {avg_fps:.1f}")
        logger.info(f"  Session duration: {total_time:.1f}s")
        
        logger.info("監視セッション完了:")
        logger.info(f"  総フレーム数: {self.stats['total_frames']}")
        logger.info(f"  総検出数: {self.stats['total_detections']}")
        logger.info(f"  平均FPS: {avg_fps:.1f}")
        logger.info(f"  セッション時間: {total_time:.1f}秒")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get current monitoring statistics.
        (現在の監視統計を取得)
        
        Returns:
            Dict[str, Any]: Current statistics (現在の統計)
        """
        current_time = time.time()
        session_time = current_time - self.stats["start_time"] if self.stats["start_time"] > 0 else 0
        
        return {
            "total_frames": self.stats["total_frames"],
            "total_detections": self.stats["total_detections"],
            "current_fps": self.stats["current_fps"],
            "session_time": session_time,
            "average_fps": self.stats["total_frames"] / session_time if session_time > 0 else 0,
            "is_running": self.is_running,
            "detection_method": self.detection_method.value,
            "position_method": self.position_method.value,
        }