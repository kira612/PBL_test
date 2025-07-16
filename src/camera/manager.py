"""
Camera input module for the monitoring system.
(監視システムのカメラ入力モジュール)
"""

import asyncio
import time
from typing import Optional, Tuple, Generator, AsyncGenerator
from pathlib import Path

import cv2
import numpy as np
from loguru import logger


class CameraManager:
    """
    Camera management class for handling video input.
    (ビデオ入力を処理するカメラ管理クラス)
    """

    def __init__(
        self,
        camera_id: int = 0,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
    ) -> None:
        """
        Initialize camera manager.
        (カメラマネージャーの初期化)
        
        Args:
            camera_id: Camera device ID (カメラデバイスID)
            width: Frame width (フレーム幅)
            height: Frame height (フレーム高さ)
            fps: Frames per second (フレームレート)
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self._frame_count = 0
        self._start_time = 0.0

    def initialize(self) -> bool:
        """
        Initialize camera device.
        (カメラデバイスの初期化)
        
        Returns:
            bool: Success status (成功状態)
        """
        try:
            # Try DirectShow backend first on Windows
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
            
            if not self.cap.isOpened():
                # Fallback to default backend
                self.cap = cv2.VideoCapture(self.camera_id)
                
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                logger.error(f"カメラ {self.camera_id} のオープンに失敗しました")
                return False
            
            # Set camera properties (カメラプロパティの設定)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Verify settings (設定の確認)
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"Camera initialized: {actual_width}x{actual_height} @ {actual_fps}fps")
            logger.info(f"カメラ初期化完了: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            self.is_running = True
            self._start_time = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            logger.error(f"カメラ初期化に失敗しました: {e}")
            return False

    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read a single frame from camera.
        (カメラから単一フレームを読み取り)
        
        Returns:
            Optional[np.ndarray]: Frame data or None if failed (フレームデータまたは失敗時はNone)
        """
        if not self.cap or not self.is_running:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera")
            logger.warning("カメラからフレームの読み取りに失敗しました")
            return None
            
        self._frame_count += 1
        return frame

    def get_frame_generator(self) -> Generator[np.ndarray, None, None]:
        """
        Generator for continuous frame reading.
        (連続フレーム読み取り用ジェネレーター)
        
        Yields:
            np.ndarray: Frame data (フレームデータ)
        """
        while self.is_running:
            frame = self.read_frame()
            if frame is not None:
                yield frame
            else:
                break

    async def get_async_frame_generator(self) -> AsyncGenerator[np.ndarray, None]:
        """
        Async generator for continuous frame reading.
        (連続フレーム読み取り用非同期ジェネレーター)
        
        Yields:
            np.ndarray: Frame data (フレームデータ)
        """
        frame_interval = 1.0 / self.fps
        
        while self.is_running:
            start_time = time.time()
            
            frame = self.read_frame()
            if frame is not None:
                yield frame
            else:
                break
                
            # Maintain target FPS (目標FPS維持)
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

    def get_camera_info(self) -> dict:
        """
        Get camera information.
        (カメラ情報の取得)
        
        Returns:
            dict: Camera information (カメラ情報)
        """
        if not self.cap:
            return {}
            
        info = {
            "camera_id": self.camera_id,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
            "frame_count": self._frame_count,
            "running_time": time.time() - self._start_time if self._start_time > 0 else 0,
            "is_running": self.is_running,
        }
        
        return info

    def get_stats(self) -> dict:
        """
        Get camera statistics.
        (カメラ統計情報の取得)
        
        Returns:
            dict: Camera statistics (カメラ統計情報)
        """
        running_time = time.time() - self._start_time if self._start_time > 0 else 0
        actual_fps = self._frame_count / running_time if running_time > 0 else 0
        
        return {
            "total_frames": self._frame_count,
            "running_time": running_time,
            "actual_fps": actual_fps,
            "target_fps": self.fps,
        }

    def stop(self) -> None:
        """
        Stop camera capture.
        (カメラキャプチャの停止)
        """
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
            
        logger.info("Camera stopped")
        logger.info("カメラが停止されました")

    def __enter__(self):
        """Context manager entry."""
        if not self.initialize():
            raise RuntimeError("Failed to initialize camera")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


class MultiCameraManager:
    """
    Multiple camera management class.
    (複数カメラ管理クラス)
    """

    def __init__(self, camera_configs: list[dict]) -> None:
        """
        Initialize multiple camera manager.
        (複数カメラマネージャーの初期化)
        
        Args:
            camera_configs: List of camera configurations (カメラ設定のリスト)
        """
        self.cameras: dict[int, CameraManager] = {}
        
        for config in camera_configs:
            camera_id = config.get("camera_id", 0)
            self.cameras[camera_id] = CameraManager(
                camera_id=camera_id,
                width=config.get("width", 640),
                height=config.get("height", 480),
                fps=config.get("fps", 30),
            )

    def initialize_all(self) -> bool:
        """
        Initialize all cameras.
        (すべてのカメラの初期化)
        
        Returns:
            bool: Success status (成功状態)
        """
        success_count = 0
        
        for camera_id, camera in self.cameras.items():
            if camera.initialize():
                success_count += 1
                logger.info(f"Camera {camera_id} initialized successfully")
                logger.info(f"カメラ {camera_id} の初期化が成功しました")
            else:
                logger.error(f"Camera {camera_id} initialization failed")
                logger.error(f"カメラ {camera_id} の初期化に失敗しました")
        
        return success_count > 0

    def get_camera(self, camera_id: int) -> Optional[CameraManager]:
        """
        Get camera manager by ID.
        (IDによるカメラマネージャーの取得)
        
        Args:
            camera_id: Camera ID (カメラID)
            
        Returns:
            Optional[CameraManager]: Camera manager or None (カメラマネージャーまたはNone)
        """
        return self.cameras.get(camera_id)

    def stop_all(self) -> None:
        """
        Stop all cameras.
        (すべてのカメラの停止)
        """
        for camera in self.cameras.values():
            camera.stop()
        
        logger.info("All cameras stopped")
        logger.info("すべてのカメラが停止されました")

    def __enter__(self):
        """Context manager entry."""
        if not self.initialize_all():
            raise RuntimeError("Failed to initialize cameras")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_all()