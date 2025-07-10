"""
Helper functions for common operations.
(qÍ\n_nØëÑü¢p)
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
    (¢¹Ú¯ÈÔ’ÝWf;Ï’êµ¤º)
    
    Args:
        image: Input image (e›;Ï)
        target_width: Target width (îE)
        target_height: Target height (îØU)
        
    Returns:
        Tuple[np.ndarray, float]: Resized image and scale factor (êµ¤ºUŒ_;Ïh¹±üëÂp)
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
    (2¹“næü¯êÃÉÝâ’—)
    
    Args:
        point1: First point (,1¹)
        point2: Second point (,2¹)
        
    Returns:
        float: Distance (Ýâ)
    """
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def bbox_center(bbox: List[float]) -> Tuple[float, float]:
    """
    Calculate center point of bounding box.
    (Ð¦óÇ£ó°ÜÃ¯¹n-Ã¹’—)
    
    Args:
        bbox: Bounding box [x1, y1, x2, y2] (Ð¦óÇ£ó°ÜÃ¯¹)
        
    Returns:
        Tuple[float, float]: Center point (x, y) (-Ã¹)
    """
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2


def bbox_area(bbox: List[float]) -> float:
    """
    Calculate area of bounding box.
    (Ð¦óÇ£ó°ÜÃ¯¹nbM’—)
    
    Args:
        bbox: Bounding box [x1, y1, x2, y2] (Ð¦óÇ£ó°ÜÃ¯¹)
        
    Returns:
        float: Area (bM)
    """
    x1, y1, x2, y2 = bbox
    return (x2 - x1) * (y2 - y1)


def bbox_iou(bbox1: List[float], bbox2: List[float]) -> float:
    """
    Calculate Intersection over Union (IoU) of two bounding boxes.
    (2dnÐ¦óÇ£ó°ÜÃ¯¹nIoU’—)
    
    Args:
        bbox1: First bounding box (,1Ð¦óÇ£ó°ÜÃ¯¹)
        bbox2: Second bounding box (,2Ð¦óÇ£ó°ÜÃ¯¹)
        
    Returns:
        float: IoU value (IoU$)
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
    (¿¤à¹¿ó×ØMnú›Ç£ì¯Èê’\)
    
    Args:
        base_path: Base directory path (Ùü¹Ç£ì¯ÈêÑ¹)
        prefix: Directory name prefix (Ç£ì¯Èê×ìÕ£Ã¯¹)
        
    Returns:
        Path: Created directory path (\UŒ_Ç£ì¯ÈêÑ¹)
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(base_path) / f"{prefix}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def fps_counter():
    """
    Simple FPS counter generator.
    (·ó×ëjFPS«¦ó¿ü¸§Íìü¿)
    
    Yields:
        float: Current FPS (þ(nFPS)
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
    (ÌoØMÆ­¹È’Ï;)
    
    Args:
        image: Input image (e›;Ï)
        text: Text to draw (Ï;Y‹Æ­¹È)
        position: Text position (Æ­¹ÈMn)
        font_scale: Font scale (Õ©óÈ¹±üë)
        color: Text color (Æ­¹Èr)
        bg_color: Background color (Ìor)
        thickness: Text thickness (Æ­¹È*U)
        
    Returns:
        np.ndarray: Image with text (Æ­¹ÈØM;Ï)
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
    (§’[0, 1]nÄòkc)
    
    Args:
        coordinates: Input coordinates (e›§)
        image_width: Image width (;ÏE)
        image_height: Image height (;ÏØU)
        
    Returns:
        Tuple[float, float]: Normalized coordinates (cUŒ_§)
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
    ([0, 1]nÄòK‰Ô¯»ë§k^c)
    
    Args:
        normalized_coords: Normalized coordinates (cUŒ_§)
        image_width: Image width (;ÏE)
        image_height: Image height (;ÏØU)
        
    Returns:
        Tuple[int, int]: Pixel coordinates (Ô¯»ë§)
    """
    x_norm, y_norm = normalized_coords
    x = int(x_norm * image_width)
    y = int(y_norm * image_height)
    return x, y


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE).
    (³óÈé¹È6PiÜÒ¹È°éàGI’i()
    
    Args:
        image: Input image (e›;Ï)
        clip_limit: Clipping limit (¯êÃÔó°6P)
        tile_grid_size: Grid size for tiles (¿¤ën°êÃÉµ¤º)
        
    Returns:
        np.ndarray: Enhanced image (7UŒ_;Ï)
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
    (¼íd—kþWfÇÕ©ëÈ$’ÔY‰hjd—)
    
    Args:
        numerator: Numerator (P)
        denominator: Denominator (Í)
        default: Default value for zero denominator (¼íd—BnÇÕ©ëÈ$)
        
    Returns:
        float: Division result or default value (d—Pœ~_oÇÕ©ëÈ$)
    """
    return numerator / denominator if denominator != 0 else default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value to specified range.
    ($’šÄòk¯éó×)
    
    Args:
        value: Input value (e›$)
        min_val: Minimum value ( $)
        max_val: Maximum value ( '$)
        
    Returns:
        float: Clamped value (¯éó×UŒ_$)
    """
    return max(min_val, min(value, max_val))