#!/usr/bin/env python3
"""
Main application entry point for camera-based monitoring system.
(カメラベース監視システムのメインアプリケーションエントリーポイント)
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import click
from loguru import logger


def setup_logging(debug: bool = False) -> None:
    """
    Setup logging configuration.
    (ログ設定のセットアップ)
    """
    log_level = "DEBUG" if debug else "INFO"
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
    )


@click.command()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode (デバッグモードを有効にする)",
)
@click.option(
    "--camera-id",
    type=int,
    default=0,
    help="Camera device ID (カメラデバイスID)",
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file (設定ファイルのパス)",
)
@click.option(
    "--display",
    type=click.Choice(['none', 'window', 'headless']),
    default='none',
    help="Display mode for visualization (可視化の表示モード)",
)
@click.option(
    "--show-fps",
    is_flag=True,
    default=True,
    help="Show FPS counter in display (表示でFPSカウンターを表示)",
)
@click.option(
    "--show-info",
    is_flag=True,
    default=True,
    help="Show detection and position info (検出と位置情報を表示)",
)
def main(debug: bool, camera_id: int, config: Optional[Path], 
         display: str, show_fps: bool, show_info: bool) -> None:
    """
    Camera-based monitoring system for laboratory environments.
    (研究室環境向けカメラベース監視システム)
    
    This system provides:
    - Person detection and tracking (人物検出と追跡)
    - Position estimation (位置推定)
    - Action recognition (行動認識)
    - Real-time monitoring dashboard (リアルタイム監視ダッシュボード)
    """
    setup_logging(debug)
    
    logger.info("Starting camera-based monitoring system...")
    logger.info("カメラベース監視システムを開始しています...")
    
    if config:
        logger.info(f"Using configuration file: {config}")
        logger.info(f"設定ファイルを使用: {config}")
    
    logger.info(f"Camera device ID: {camera_id}")
    logger.info(f"カメラデバイスID: {camera_id}")
    
    try:
        # Initialize the monitoring system (監視システムの初期化)
        # TODO: Implement actual monitoring system initialization
        # TODO: 実際の監視システム初期化を実装
        
        logger.info("System initialized successfully")
        logger.info("システムが正常に初期化されました")
        
        # Run the main application loop (メインアプリケーションループの実行)
        asyncio.run(run_monitoring_system(camera_id, config, display, show_fps, show_info))
        
    except KeyboardInterrupt:
        logger.info("Shutting down system...")
        logger.info("システムをシャットダウンしています...")
    except Exception as e:
        logger.error(f"System error: {e}")
        logger.error(f"システムエラー: {e}")
        raise


async def run_monitoring_system(camera_id: int, config: Optional[Path], 
                               display: str, show_fps: bool, show_info: bool) -> None:
    """
    Run the main monitoring system loop.
    (メイン監視システムループの実行)
    """
    from src.core.coordinator import MonitoringCoordinator
    from src.core.detector import DetectionMethod
    from src.vision.position_estimator import PositionMethod
    from src.visualization.display import create_display_config
    
    logger.info("Monitoring system is running...")
    logger.info("監視システムが実行中です...")
    
    # Create display configuration
    display_config = create_display_config(
        mode=display,
        show_fps=show_fps,
        show_detection_count=show_info,
        show_position_info=show_info,
        show_action_info=show_info
    )
    
    # Initialize monitoring coordinator
    coordinator = MonitoringCoordinator(
        camera_id=camera_id,
        config_path=config,
        detection_method=DetectionMethod.YOLO,  # Can be changed to MEDIAPIPE
        position_method=PositionMethod.BBOX_CENTER,  # Can be changed to PERSPECTIVE_MAPPING
        display_config=display_config
    )
    
    # Initialize system components
    if not await coordinator.initialize():
        logger.error("Failed to initialize monitoring system")
        logger.error("監視システムの初期化に失敗しました")
        return
    
    try:
        # Start the monitoring loop
        await coordinator.start_monitoring()
    except Exception as e:
        logger.error(f"Monitoring system error: {e}")
        logger.error(f"監視システムエラー: {e}")
    finally:
        # Ensure proper cleanup
        await coordinator.stop_monitoring()


if __name__ == "__main__":
    main()