"""
Configuration management for the monitoring system.
(監視システムの設定管理)
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class CameraConfig:
    """Camera configuration."""
    camera_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30


@dataclass
class RoomConfig:
    """Room configuration."""
    width: float = 4.0  # meters
    height: float = 3.0  # meters
    camera_height: float = 2.5  # meters


@dataclass
class DetectionConfig:
    """Detection configuration."""
    method: str = "yolo"  # "yolo" or "mediapipe"
    confidence_threshold: float = 0.5
    yolo_model_path: str = "yolov8n.pt"


@dataclass
class PositionConfig:
    """Position estimation configuration."""
    method: str = "bbox_center"  # "bbox_center", "perspective_mapping", "depth_estimation"
    calibration_points: Optional[list] = None  # For perspective mapping


@dataclass
class ActionConfig:
    """Action recognition configuration."""
    use_pose: bool = True
    confidence_threshold: float = 0.3


@dataclass
class DisplayConfig:
    """Display configuration."""
    mode: str = "none"  # "none", "window", "headless"
    window_name: str = "Laboratory Monitoring System"
    show_fps: bool = True
    show_detection_count: bool = True
    show_position_info: bool = True
    show_action_info: bool = True


@dataclass
class SystemConfig:
    """System configuration."""
    display_enabled: bool = True
    save_results: bool = False
    output_directory: str = "output"
    log_level: str = "INFO"


@dataclass
class Config:
    """Main configuration class."""
    camera: CameraConfig
    room: RoomConfig
    detection: DetectionConfig
    position: PositionConfig
    action: ActionConfig
    display: DisplayConfig
    system: SystemConfig

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """
        Load configuration from file.
        (ファイルから設定を読み込み)
        
        Args:
            config_path: Path to configuration file (設定ファイルのパス)
            
        Returns:
            Config: Configuration instance (設定インスタンス)
        """
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            logger.warning(f"設定ファイルが見つかりません: {config_path}")
            return cls.default()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    data = json.load(f)
                elif config_path.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                else:
                    logger.error(f"Unsupported config file format: {config_path.suffix}")
                    return cls.default()
            
            return cls.from_dict(data)
            
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            logger.error(f"設定ファイルの読み込みに失敗: {e}")
            return cls.default()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Create configuration from dictionary.
        (辞書から設定を作成)
        
        Args:
            data: Configuration data (設定データ)
            
        Returns:
            Config: Configuration instance (設定インスタンス)
        """
        try:
            return cls(
                camera=CameraConfig(**data.get("camera", {})),
                room=RoomConfig(**data.get("room", {})),
                detection=DetectionConfig(**data.get("detection", {})),
                position=PositionConfig(**data.get("position", {})),
                action=ActionConfig(**data.get("action", {})),
                display=DisplayConfig(**data.get("display", {})),
                system=SystemConfig(**data.get("system", {}))
            )
        except Exception as e:
            logger.error(f"Failed to create config from dict: {e}")
            logger.error(f"辞書から設定の作成に失敗: {e}")
            return cls.default()
    
    @classmethod
    def default(cls) -> "Config":
        """
        Create default configuration.
        (デフォルト設定を作成)
        
        Returns:
            Config: Default configuration (デフォルト設定)
        """
        return cls(
            camera=CameraConfig(),
            room=RoomConfig(),
            detection=DetectionConfig(),
            position=PositionConfig(),
            action=ActionConfig(),
            display=DisplayConfig(),
            system=SystemConfig()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        (設定を辞書に変換)
        
        Returns:
            Dict[str, Any]: Configuration dictionary (設定辞書)
        """
        return {
            "camera": asdict(self.camera),
            "room": asdict(self.room),
            "detection": asdict(self.detection),
            "position": asdict(self.position),
            "action": asdict(self.action),
            "display": asdict(self.display),
            "system": asdict(self.system)
        }
    
    def save_to_file(self, config_path: Path) -> bool:
        """
        Save configuration to file.
        (設定をファイルに保存)
        
        Args:
            config_path: Path to save configuration (設定保存パス)
            
        Returns:
            bool: Success status (成功状態)
        """
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
                elif config_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(self.to_dict(), f, default_flow_style=False, 
                             allow_unicode=True, sort_keys=False)
                else:
                    logger.error(f"Unsupported config file format: {config_path.suffix}")
                    return False
            
            logger.info(f"Configuration saved to: {config_path}")
            logger.info(f"設定を保存しました: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")
            logger.error(f"設定ファイルの保存に失敗: {e}")
            return False


def create_sample_config() -> Config:
    """
    Create sample configuration for testing.
    (テスト用のサンプル設定を作成)
    
    Returns:
        Config: Sample configuration (サンプル設定)
    """
    return Config(
        camera=CameraConfig(
            camera_id=0,
            width=640,
            height=480,
            fps=30
        ),
        room=RoomConfig(
            width=4.0,
            height=3.0,
            camera_height=2.5
        ),
        detection=DetectionConfig(
            method="yolo",
            confidence_threshold=0.6,
            yolo_model_path="yolov8n.pt"
        ),
        position=PositionConfig(
            method="bbox_center",
            calibration_points=None
        ),
        action=ActionConfig(
            use_pose=True,
            confidence_threshold=0.3
        ),
        display=DisplayConfig(
            mode="window",
            window_name="Laboratory Monitoring System",
            show_fps=True,
            show_detection_count=True,
            show_position_info=True,
            show_action_info=True
        ),
        system=SystemConfig(
            display_enabled=True,
            save_results=False,
            output_directory="output",
            log_level="INFO"
        )
    )