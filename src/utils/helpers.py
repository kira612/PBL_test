"""
Helper functions for common operations.
(共通操作のためのヘルパー関数)
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Union
from pathlib import Path
import time
import datetime
from loguru import logger


def resize_image_keep_aspect(
    image: np.ndarray,
    target_width: int,
    target_height: int
) -> Tuple[np.ndarray, float]:
    """
    Resize image while keeping aspect ratio.
    (アスペクト比を保持して画像をリサイズ)
    
    Args:
        image: Input image (入力画像)
        target_width: Target width (目標幅)
        target_height: Target height (目標高さ)
        
    Returns:
        Tuple[np.ndarray, float]: Resized image and scale factor (リサイズされた画像とスケール係数)
    """
    h, w = image.shape[:2]
    scale = min(target_width / w, target_height / h)
    
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    resized = cv2.resize(image, (new_w, new_h))
    
    # Create padded image
    result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    y_offset = (target_height - new_h) // 2
    x_offset = (target_width - new_w) // 2
    result[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
    
    return result, scale


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points.
    (2点間のユークリッド距離を計算)
    
    Args:
        point1: First point (第1点)
        point2: Second point (第2点)
        
    Returns:
        float: Distance (距離)
    """
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def bbox_center(bbox: List[float]) -> Tuple[float, float]:
    """
    Calculate center point of bounding box.
    (バウンディングボックスの中心点を計算)
    
    Args:
        bbox: Bounding box [x1, y1, x2, y2] (バウンディングボックス)
        
    Returns:
        Tuple[float, float]: Center point (x, y) (中心点)
    """
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2


def bbox_area(bbox: List[float]) -> float:
    """
    Calculate area of bounding box.
    (バウンディングボックスの面積を計算)
    
    Args:
        bbox: Bounding box [x1, y1, x2, y2] (バウンディングボックス)
        
    Returns:
        float: Area (面積)
    """
    x1, y1, x2, y2 = bbox
    return (x2 - x1) * (y2 - y1)


def bbox_iou(bbox1: List[float], bbox2: List[float]) -> float:
    """
    Calculate Intersection over Union (IoU) of two bounding boxes.
    (2つのバウンディングボックスのIoUを計算)
    
    Args:
        bbox1: First bounding box (第1バウンディングボックス)
        bbox2: Second bounding box (第2バウンディングボックス)
        
    Returns:
        float: IoU value (IoU値)
    """
    x1_1, y1_1, x2_1, y2_1 = bbox1
    x1_2, y1_2, x2_2, y2_2 = bbox2
    
    # Calculate intersection
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i <= x1_i or y2_i <= y1_i:
        return 0.0
    
    intersection = (x2_i - x1_i) * (y2_i - y1_i)
    area1 = bbox_area(bbox1)
    area2 = bbox_area(bbox2)
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0


def create_output_directory(base_path: str, prefix: str = "run") -> Path:
    """
    Create output directory with timestamp.
    (タイムスタンプ付きの出力ディレクトリを作成)
    
    Args:
        base_path: Base directory path (ベースディレクトリパス)
        prefix: Directory name prefix (ディレクトリ名プレフィックス)
        
    Returns:
        Path: Created directory path (作成されたディレクトリパス)
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(base_path) / f"{prefix}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def fps_counter():
    """
    Simple FPS counter generator.
    (シンプルなFPSカウンタージェネレーター)
    
    Yields:
        float: Current FPS (現在のFPS)
    """
    start_time = time.time()
    frame_count = 0
    
    while True:
        frame_count += 1
        elapsed = time.time() - start_time
        
        if elapsed >= 1.0:
            fps = frame_count / elapsed
            frame_count = 0
            start_time = time.time()
            yield fps
        else:
            yield 0.0


def draw_text_with_background(
    image: np.ndarray,
    text: str,
    position: Tuple[int, int],
    font_scale: float = 0.7,
    color: Tuple[int, int, int] = (255, 255, 255),
    bg_color: Tuple[int, int, int] = (0, 0, 0),
    thickness: int = 2
) -> np.ndarray:
    """
    Draw text with background rectangle.
    (背景付きテキストを描画)
    
    Args:
        image: Input image (入力画像)
        text: Text to draw (描画するテキスト)
        position: Text position (テキスト位置)
        font_scale: Font scale (フォントスケール)
        color: Text color (テキスト色)
        bg_color: Background color (背景色)
        thickness: Text thickness (テキスト太さ)
        
    Returns:
        np.ndarray: Image with text (テキスト付き画像)
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Draw background rectangle
    x, y = position
    cv2.rectangle(
        image,
        (x, y - text_height - baseline),
        (x + text_width, y + baseline),
        bg_color,
        -1
    )
    
    # Draw text
    cv2.putText(image, text, position, font, font_scale, color, thickness)
    
    return image


def normalize_coordinates(
    coordinates: Union[Tuple[float, float], List[float]],
    image_width: int,
    image_height: int
) -> Tuple[float, float]:
    """
    Normalize coordinates to [0, 1] range.
    (座標を[0, 1]の範囲に正規化)
    
    Args:
        coordinates: Input coordinates (入力座標)
        image_width: Image width (画像幅)
        image_height: Image height (画像高さ)
        
    Returns:
        Tuple[float, float]: Normalized coordinates (正規化された座標)
    """
    if isinstance(coordinates, (list, tuple)) and len(coordinates) >= 2:
        x, y = coordinates[0], coordinates[1]
        return x / image_width, y / image_height
    else:
        raise ValueError("Invalid coordinates format")


def denormalize_coordinates(
    normalized_coords: Tuple[float, float],
    image_width: int,
    image_height: int
) -> Tuple[int, int]:
    """
    Denormalize coordinates from [0, 1] range to pixel coordinates.
    ([0, 1]の範囲からピクセル座標に非正規化)
    
    Args:
        normalized_coords: Normalized coordinates (正規化された座標)
        image_width: Image width (画像幅)
        image_height: Image height (画像高さ)
        
    Returns:
        Tuple[int, int]: Pixel coordinates (ピクセル座標)
    """
    x_norm, y_norm = normalized_coords
    x = int(x_norm * image_width)
    y = int(y_norm * image_height)
    return x, y


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE).
    (コントラスト制限適応ヒストグラム均等化を適用)
    
    Args:
        image: Input image (入力画像)
        clip_limit: Clipping limit (クリッピング制限)
        tile_grid_size: Grid size for tiles (タイルのグリッドサイズ)
        
    Returns:
        np.ndarray: Enhanced image (強化された画像)
    """
    if len(image.shape) == 3:
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l_channel = clahe.apply(l_channel)
        
        # Merge channels and convert back to BGR
        lab = cv2.merge([l_channel, a_channel, b_channel])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    else:
        # Grayscale image
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division with default value for zero denominator.
    (ゼロ除算に対してデフォルト値を返す安全な除算)
    
    Args:
        numerator: Numerator (分子)
        denominator: Denominator (分母)
        default: Default value for zero denominator (ゼロ除算時のデフォルト値)
        
    Returns:
        float: Division result or default value (除算結果またはデフォルト値)
    """
    return numerator / denominator if denominator != 0 else default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value to specified range.
    (値を指定範囲にクランプ)
    
    Args:
        value: Input value (入力値)
        min_val: Minimum value (最小値)
        max_val: Maximum value (最大値)
        
    Returns:
        float: Clamped value (クランプされた値)
    """
    return max(min_val, min(value, max_val))