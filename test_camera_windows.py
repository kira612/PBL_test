#!/usr/bin/env python3
"""
Windows Camera Access Test Script
Windowsでのカメラアクセステストスクリプト
"""

import cv2
import sys
import platform

def test_camera_access():
    """Test camera access on Windows"""
    print(f"Platform: {platform.system()}")
    print(f"Python version: {sys.version}")
    print(f"OpenCV version: {cv2.__version__}")
    
    # Try to access default camera (usually index 0)
    print("\nTrying to access camera...")
    
    # For Windows, try DirectShow backend
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("❌ Failed to open camera with DirectShow backend")
        
        # Try default backend
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Failed to open camera with default backend")
            return False
        else:
            print("✅ Camera opened with default backend")
    else:
        print("✅ Camera opened with DirectShow backend")
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Camera resolution: {width}x{height}")
    print(f"Camera FPS: {fps}")
    
    # Try to capture a frame
    ret, frame = cap.read()
    
    if ret:
        print("✅ Successfully captured a frame")
        print(f"Frame shape: {frame.shape}")
        
        # Save test image
        cv2.imwrite("test_capture.jpg", frame)
        print("📸 Test image saved as 'test_capture.jpg'")
        
    else:
        print("❌ Failed to capture frame")
        cap.release()
        return False
    
    cap.release()
    print("✅ Camera test completed successfully")
    return True

if __name__ == "__main__":
    success = test_camera_access()
    sys.exit(0 if success else 1)