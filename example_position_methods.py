#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of different position estimation methods.
(異なる位置推定手法の使用例)
"""

import cv2
import numpy as np
from src.vision.position_manager import PositionEstimationManager
from src.core.position_interface import PositionMethod, RoomDimensions
from src.core.detector import Detection

def create_example_detection():
    """Create example detection for testing."""
    return Detection(
        bbox=[100, 50, 80, 200],  # x, y, w, h
        confidence=0.85,
        class_id=0,
        class_name="person"
    )

def create_example_frame():
    """Create example frame for testing."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw a simple person-like rectangle
    cv2.rectangle(frame, (100, 50), (180, 250), (255, 255, 255), -1)
    return frame

def demonstrate_perspective_mapping():
    """Demonstrate perspective mapping method."""
    print("=== Perspective Mapping Method ===")
    
    estimator = PositionEstimationManager(
        method=PositionMethod.PERSPECTIVE_MAPPING,
        room_dimensions=RoomDimensions(width=4.0, height=3.0),
        frame_width=640,
        frame_height=480
    )
    
    detection = create_example_detection()
    positions = estimator.estimate_positions([detection])
    
    if positions:
        pos = positions[0]
        print(f"Position: ({pos.x:.2f}m, {pos.y:.2f}m)")
        print(f"Confidence: {pos.confidence:.2f}")
    else:
        print("No position estimated")
    print()

def demonstrate_mediapipe_pose():
    """Demonstrate MediaPipe pose estimation method."""
    print("=== MediaPipe Pose Method ===")
    
    try:
        estimator = PositionEstimationManager(
            method=PositionMethod.MEDIAPIPE_POSE,
            room_dimensions=RoomDimensions(width=4.0, height=3.0),
            frame_width=640,
            frame_height=480
        )
        
        detection = create_example_detection()
        frame = create_example_frame()
        positions = estimator.estimate_positions([detection], frame=frame)
        
        if positions:
            pos = positions[0]
            print(f"Position: ({pos.x:.2f}m, {pos.y:.2f}m)")
            print(f"Confidence: {pos.confidence:.2f}")
        else:
            print("No position estimated")
            
    except ImportError as e:
        print(f"MediaPipe not available: {e}")
        print("Install with: pip install mediapipe")
    print()

def demonstrate_midas_depth():
    """Demonstrate MiDaS depth estimation method."""
    print("=== MiDaS Depth Method ===")
    
    try:
        estimator = PositionEstimationManager(
            method=PositionMethod.MIDAS_DEPTH,
            room_dimensions=RoomDimensions(width=4.0, height=3.0),
            frame_width=640,
            frame_height=480
        )
        
        detection = create_example_detection()
        frame = create_example_frame()
        positions = estimator.estimate_positions([detection], frame=frame)
        
        if positions:
            pos = positions[0]
            print(f"Position: ({pos.x:.2f}m, {pos.y:.2f}m)")
            print(f"Confidence: {pos.confidence:.2f}")
        else:
            print("No position estimated")
            
    except ImportError as e:
        print(f"PyTorch not available: {e}")
        print("Install with: pip install torch torchvision")
    except Exception as e:
        print(f"MiDaS model loading failed: {e}")
        print("First run may take time to download the model")
    print()

def demonstrate_dpt_depth():
    """Demonstrate DPT depth estimation method."""
    print("=== DPT Depth Method ===")
    
    try:
        estimator = PositionEstimationManager(
            method=PositionMethod.DPT_DEPTH,
            room_dimensions=RoomDimensions(width=4.0, height=3.0),
            frame_width=640,
            frame_height=480
        )
        
        detection = create_example_detection()
        frame = create_example_frame()
        positions = estimator.estimate_positions([detection], frame=frame)
        
        if positions:
            pos = positions[0]
            print(f"Position: ({pos.x:.2f}m, {pos.y:.2f}m)")
            print(f"Confidence: {pos.confidence:.2f}")
        else:
            print("No position estimated")
            
    except ImportError as e:
        print(f"Transformers not available: {e}")
        print("Install with: pip install transformers")
    except Exception as e:
        print(f"DPT model loading failed: {e}")
        print("First run may take time to download the model")
    print()

def compare_all_methods():
    """Compare all available position estimation methods."""
    print("=== Comparison of All Methods ===")
    
    detection = create_example_detection()
    frame = create_example_frame()
    
    methods = [
        PositionMethod.BBOX_CENTER,
        PositionMethod.PERSPECTIVE_MAPPING,
        PositionMethod.DEPTH_ESTIMATION,
        PositionMethod.MEDIAPIPE_POSE,
        PositionMethod.MIDAS_DEPTH,
        PositionMethod.DPT_DEPTH
    ]
    
    results = {}
    
    for method in methods:
        try:
            estimator = PositionEstimationManager(
                method=method,
                room_dimensions=RoomDimensions(width=4.0, height=3.0),
                frame_width=640,
                frame_height=480
            )
            
            if method in [PositionMethod.MEDIAPIPE_POSE, PositionMethod.MIDAS_DEPTH, PositionMethod.DPT_DEPTH]:
                positions = estimator.estimate_positions([detection], frame=frame)
            else:
                positions = estimator.estimate_positions([detection])
            
            if positions:
                pos = positions[0]
                results[method.value] = {
                    'position': (pos.x, pos.y),
                    'confidence': pos.confidence
                }
            else:
                results[method.value] = {'error': 'No position estimated'}
                
        except Exception as e:
            results[method.value] = {'error': str(e)}
    
    # Display results
    print(f"{'Method':<20} {'X (m)':<8} {'Y (m)':<8} {'Confidence':<12} {'Status'}")
    print("-" * 65)
    
    for method_name, result in results.items():
        if 'error' in result:
            print(f"{method_name:<20} {'N/A':<8} {'N/A':<8} {'N/A':<12} {result['error']}")
        else:
            x, y = result['position']
            conf = result['confidence']
            print(f"{method_name:<20} {x:<8.2f} {y:<8.2f} {conf:<12.2f} {'Success'}")

def main():
    """Main demonstration function."""
    print("Position Estimation Methods Demonstration")
    print("位置推定手法のデモンストレーション")
    print("=" * 50)
    print()
    
    # Demonstrate each method individually
    demonstrate_perspective_mapping()
    demonstrate_mediapipe_pose()
    demonstrate_midas_depth()
    demonstrate_dpt_depth()
    
    # Compare all methods
    compare_all_methods()
    
    print("\nTo use in your application:")
    print("アプリケーションでの使用方法:")
    print("""
from src.vision.position_manager import PositionEstimationManager
from src.core.position_interface import PositionMethod

# Choose your method (選択する手法):
# - PositionMethod.PERSPECTIVE_MAPPING (透視変換)
# - PositionMethod.MEDIAPIPE_POSE (MediaPipeポーズ推定)
# - PositionMethod.MIDAS_DEPTH (MiDaS深度推定)
# - PositionMethod.DPT_DEPTH (DPT深度推定)

estimator = PositionEstimationManager(
    method=PositionMethod.MEDIAPIPE_POSE,  # Change this (これを変更)
    frame_width=640,
    frame_height=480
)

# For methods that need frame data (フレームデータが必要な手法用):
positions = estimator.estimate_positions(detections, frame=frame)

# For methods that only need detection data (検出データのみが必要な手法用):
positions = estimator.estimate_positions(detections)
""")

if __name__ == "__main__":
    main()