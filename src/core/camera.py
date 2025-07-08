"""
Camera input module for the monitoring system.
(ã–·¹Æàn«áée›â¸åüë)
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
    (ÓÇªe›’æY‹_n«áé¡¯é¹)
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
        («áéÞÍü¸ãün)
        
        Args:
            camera_id: Camera device ID («áéÇÐ¤¹ID)
            width: Frame width (ÕìüàE)
            height: Frame height (ÕìüàØU)
            fps: Frames per second (ÕìüàìüÈ)
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
        («áéÇÐ¤¹n)
        
        Returns:
            bool: Success status (Ÿ¹Æü¿¹)
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                logger.error(f"«áé {self.camera_id} ’‹Q~[“gW_")
                return False
            
            # Set camera properties («áé×íÑÆ£n-š)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Verify settings (-šnº)
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"Camera initialized: {actual_width}x{actual_height} @ {actual_fps}fps")
            logger.info(f"«áéŒ†: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            self.is_running = True
            self._start_time = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            logger.error(f"«áék1WW~W_: {e}")
            return False

    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read a single frame from camera.
        («áéK‰1Õìüà’­ÖŠ)
        
        Returns:
            Optional[np.ndarray]: Frame data or None if failed (ÕìüàÇü¿~_o1WBNone)
        """
        if not self.cap or not self.is_running:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera")
            logger.warning("«áéK‰Õìüà’­ÖŒ~[“gW_")
            return None
            
        self._frame_count += 1
        return frame

    def get_frame_generator(self) -> Generator[np.ndarray, None, None]:
        """
        Generator for continuous frame reading.
        (#šÕìüà­ÖŠn¸§Íìü¿)
        
        Yields:
            np.ndarray: Frame data (ÕìüàÇü¿)
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
        (#šÕìüà­ÖŠn^¸§Íìü¿)
        
        Yields:
            np.ndarray: Frame data (ÕìüàÇü¿)
        """
        frame_interval = 1.0 / self.fps
        
        while self.is_running:
            start_time = time.time()
            
            frame = self.read_frame()
            if frame is not None:
                yield frame
            else:
                break
                
            # Maintain target FPS (îFPS’­)
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

    def get_camera_info(self) -> dict:
        """
        Get camera information.
        («áéÅ1nÖ—)
        
        Returns:
            dict: Camera information («áéÅ1)
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
        («áéqÅ1nÖ—)
        
        Returns:
            dict: Camera statistics («áéqÅ1)
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
        («áé­ã×Áãn\b)
        """
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
            
        logger.info("Camera stopped")
        logger.info("«áé’\bW~W_")

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
    (p«áé¡¯é¹)
    """

    def __init__(self, camera_configs: list[dict]) -> None:
        """
        Initialize multiple camera manager.
        (p«áéÞÍü¸ãün)
        
        Args:
            camera_configs: List of camera configurations («áé-šnê¹È)
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
        (Yyfn«áén)
        
        Returns:
            bool: Success status (Ÿ¹Æü¿¹)
        """
        success_count = 0
        
        for camera_id, camera in self.cameras.items():
            if camera.initialize():
                success_count += 1
                logger.info(f"Camera {camera_id} initialized successfully")
                logger.info(f"«áé {camera_id} nkŸW~W_")
            else:
                logger.error(f"Camera {camera_id} initialization failed")
                logger.error(f"«áé {camera_id} nk1WW~W_")
        
        return success_count > 0

    def get_camera(self, camera_id: int) -> Optional[CameraManager]:
        """
        Get camera manager by ID.
        (IDkˆ‹«áéÞÍü¸ãünÖ—)
        
        Args:
            camera_id: Camera ID («áéID)
            
        Returns:
            Optional[CameraManager]: Camera manager or None («áéÞÍü¸ãü~_oNone)
        """
        return self.cameras.get(camera_id)

    def stop_all(self) -> None:
        """
        Stop all cameras.
        (Yyfn«áén\b)
        """
        for camera in self.cameras.values():
            camera.stop()
        
        logger.info("All cameras stopped")
        logger.info("Yyfn«áé’\bW~W_")

    def __enter__(self):
        """Context manager entry."""
        if not self.initialize_all():
            raise RuntimeError("Failed to initialize cameras")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_all()