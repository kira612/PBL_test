"""
Action recognition module for laboratory monitoring.
(研究室監視のための行動認識モジュール)
"""

import time
import math
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from loguru import logger

from ..core.detector import Detection, PersonPose


class ActionType(Enum):
    """Action type enumeration."""
    STANDING = "standing"
    SITTING = "sitting"
    COMPUTER_INTERACTION = "computer_interaction"
    WALKING = "walking"
    UNKNOWN = "unknown"


@dataclass
class ActionResult:
    """
    Action recognition result.
    (行動認識結果)
    """
    action_type: ActionType
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    timestamp: float
    details: Dict[str, Any]  # Additional action-specific details


class PoseActionRecognizer:
    """
    Action recognizer using pose landmarks.
    (ポーズランドマークを使用した行動認識器)
    """
    
    def __init__(self):
        """Initialize pose action recognizer."""
        self.standing_threshold = 0.3  # Threshold for standing vs sitting
        self.computer_interaction_threshold = 0.7  # Threshold for computer interaction
        
        # MediaPipe pose landmark indices
        # (MediaPipeポーズランドマークインデックス)
        self.landmark_indices = {
            'nose': 0,
            'left_eye': 1,
            'right_eye': 2,
            'left_ear': 3,
            'right_ear': 4,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28
        }
    
    def recognize_action(self, pose: PersonPose, frame_shape: Tuple[int, int]) -> ActionResult:
        """
        Recognize action from pose landmarks.
        (ポーズランドマークから行動認識)
        
        Args:
            pose: Person pose information (人物ポーズ情報)
            frame_shape: Frame shape (height, width) (フレーム形状)
            
        Returns:
            ActionResult: Action recognition result (行動認識結果)
        """
        height, width = frame_shape
        landmarks = pose.landmarks
        visibility = pose.visibility
        
        # Extract key landmarks
        key_landmarks = self._extract_key_landmarks(landmarks, visibility, width, height)
        
        if not key_landmarks:
            return ActionResult(
                action_type=ActionType.UNKNOWN,
                confidence=0.0,
                bbox=pose.bbox,
                timestamp=time.time(),
                details={}
            )
        
        # Analyze pose for different actions
        sitting_confidence = self._analyze_sitting_pose(key_landmarks)
        standing_confidence = self._analyze_standing_pose(key_landmarks)
        computer_confidence = self._analyze_computer_interaction(key_landmarks)
        walking_confidence = self._analyze_walking_pose(key_landmarks)
        
        # Determine primary action
        confidences = {
            ActionType.SITTING: sitting_confidence,
            ActionType.STANDING: standing_confidence,
            ActionType.COMPUTER_INTERACTION: computer_confidence,
            ActionType.WALKING: walking_confidence
        }
        
        # Get action with highest confidence
        best_action = max(confidences, key=confidences.get)
        best_confidence = confidences[best_action]
        
        # If confidence is too low, mark as unknown
        if best_confidence < 0.3:
            best_action = ActionType.UNKNOWN
            best_confidence = 0.0
        
        return ActionResult(
            action_type=best_action,
            confidence=best_confidence,
            bbox=pose.bbox,
            timestamp=time.time(),
            details={
                'all_confidences': confidences,
                'key_landmarks': key_landmarks
            }
        )
    
    def _extract_key_landmarks(
        self, 
        landmarks: List[Tuple[float, float]], 
        visibility: List[float],
        width: int, 
        height: int
    ) -> Dict[str, Tuple[float, float]]:
        """
        Extract key landmarks with good visibility.
        (良好な可視性を持つキーランドマークを抽出)
        """
        key_landmarks = {}
        
        for name, index in self.landmark_indices.items():
            if index < len(landmarks) and index < len(visibility):
                if visibility[index] > 0.5:  # Only use visible landmarks
                    x, y = landmarks[index]
                    key_landmarks[name] = (x * width, y * height)
        
        return key_landmarks
    
    def _analyze_sitting_pose(self, landmarks: Dict[str, Tuple[float, float]]) -> float:
        """
        Analyze sitting pose characteristics.
        (座位姿勢の特徴を分析)
        """
        confidence = 0.0
        
        # Check if required landmarks are available
        required_landmarks = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
        if not all(landmark in landmarks for landmark in required_landmarks):
            return confidence
        
        # Calculate shoulder and hip positions
        left_shoulder = landmarks['left_shoulder']
        right_shoulder = landmarks['right_shoulder']
        left_hip = landmarks['left_hip']
        right_hip = landmarks['right_hip']
        
        # Calculate average positions
        shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
        hip_y = (left_hip[1] + right_hip[1]) / 2
        
        # Sitting: shoulders and hips should be at similar heights
        shoulder_hip_distance = abs(shoulder_y - hip_y)
        
        # Normalize distance (smaller distance = more likely sitting)
        if shoulder_hip_distance < 50:  # pixels
            confidence += 0.6
        elif shoulder_hip_distance < 100:
            confidence += 0.3
        
        # Check if knees are visible and bent
        if 'left_knee' in landmarks and 'right_knee' in landmarks:
            left_knee = landmarks['left_knee']
            right_knee = landmarks['right_knee']
            
            # Knees should be higher than hips when sitting
            if left_knee[1] > hip_y or right_knee[1] > hip_y:
                confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _analyze_standing_pose(self, landmarks: Dict[str, Tuple[float, float]]) -> float:
        """
        Analyze standing pose characteristics.
        (立位姿勢の特徴を分析)
        """
        confidence = 0.0
        
        # Check if required landmarks are available
        required_landmarks = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
        if not all(landmark in landmarks for landmark in required_landmarks):
            return confidence
        
        # Calculate shoulder and hip positions
        left_shoulder = landmarks['left_shoulder']
        right_shoulder = landmarks['right_shoulder']
        left_hip = landmarks['left_hip']
        right_hip = landmarks['right_hip']
        
        # Calculate average positions
        shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
        hip_y = (left_hip[1] + right_hip[1]) / 2
        
        # Standing: shoulders should be significantly higher than hips
        shoulder_hip_distance = hip_y - shoulder_y
        
        if shoulder_hip_distance > 100:  # pixels
            confidence += 0.7
        elif shoulder_hip_distance > 50:
            confidence += 0.4
        
        # Check if ankles are visible and aligned
        if 'left_ankle' in landmarks and 'right_ankle' in landmarks:
            left_ankle = landmarks['left_ankle']
            right_ankle = landmarks['right_ankle']
            
            # Ankles should be below hips when standing
            if left_ankle[1] > hip_y and right_ankle[1] > hip_y:
                confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _analyze_computer_interaction(self, landmarks: Dict[str, Tuple[float, float]]) -> float:
        """
        Analyze computer interaction pose characteristics.
        (コンピューター操作姿勢の特徴を分析)
        """
        confidence = 0.0
        
        # Check if required landmarks are available
        required_landmarks = ['left_wrist', 'right_wrist', 'left_elbow', 'right_elbow']
        if not all(landmark in landmarks for landmark in required_landmarks):
            return confidence
        
        left_wrist = landmarks['left_wrist']
        right_wrist = landmarks['right_wrist']
        left_elbow = landmarks['left_elbow']
        right_elbow = landmarks['right_elbow']
        
        # Computer interaction: wrists should be in front of body and close together
        wrist_distance = math.sqrt(
            (left_wrist[0] - right_wrist[0])**2 + 
            (left_wrist[1] - right_wrist[1])**2
        )
        
        # Wrists close together (typing position)
        if wrist_distance < 100:  # pixels
            confidence += 0.5
        
        # Check elbow angles (should be bent for typing)
        if 'left_shoulder' in landmarks and 'right_shoulder' in landmarks:
            left_shoulder = landmarks['left_shoulder']
            right_shoulder = landmarks['right_shoulder']
            
            # Calculate elbow angles
            left_elbow_angle = self._calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_elbow_angle = self._calculate_angle(right_shoulder, right_elbow, right_wrist)
            
            # Ideal typing angle is around 90 degrees
            if 60 <= left_elbow_angle <= 120:
                confidence += 0.2
            if 60 <= right_elbow_angle <= 120:
                confidence += 0.2
        
        # Check if person is likely sitting (computer interaction often involves sitting)
        sitting_confidence = self._analyze_sitting_pose(landmarks)
        if sitting_confidence > 0.5:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _analyze_walking_pose(self, landmarks: Dict[str, Tuple[float, float]]) -> float:
        """
        Analyze walking pose characteristics.
        (歩行姿勢の特徴を分析)
        """
        confidence = 0.0
        
        # Check if required landmarks are available
        required_landmarks = ['left_hip', 'right_hip', 'left_knee', 'right_knee']
        if not all(landmark in landmarks for landmark in required_landmarks):
            return confidence
        
        left_hip = landmarks['left_hip']
        right_hip = landmarks['right_hip']
        left_knee = landmarks['left_knee']
        right_knee = landmarks['right_knee']
        
        # Walking: one leg should be more forward than the other
        left_leg_forward = left_knee[1] - left_hip[1]
        right_leg_forward = right_knee[1] - right_hip[1]
        
        # Check for asymmetric leg positions
        leg_difference = abs(left_leg_forward - right_leg_forward)
        if leg_difference > 30:  # pixels
            confidence += 0.5
        
        # Check if ankles are visible and in walking position
        if 'left_ankle' in landmarks and 'right_ankle' in landmarks:
            left_ankle = landmarks['left_ankle']
            right_ankle = landmarks['right_ankle']
            
            # One ankle should be more forward than the other
            ankle_difference = abs(left_ankle[1] - right_ankle[1])
            if ankle_difference > 20:  # pixels
                confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _calculate_angle(self, p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """
        Calculate angle between three points.
        (3点間の角度を計算)
        """
        # Vector from p2 to p1
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        # Vector from p2 to p3
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        # Calculate angle using dot product
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        magnitude_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
        magnitude_v2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if magnitude_v1 == 0 or magnitude_v2 == 0:
            return 0.0
        
        cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to valid range
        
        angle = math.acos(cos_angle)
        return math.degrees(angle)


class BBoxActionRecognizer:
    """
    Action recognizer using bounding box information.
    (バウンディングボックス情報を使用した行動認識器)
    """
    
    def __init__(self):
        """Initialize bbox action recognizer."""
        self.previous_positions = []  # Store previous positions for movement analysis
        self.max_history = 10  # Maximum history length
        
    def recognize_action(self, detection: Detection, frame_shape: Tuple[int, int]) -> ActionResult:
        """
        Recognize action from bounding box information.
        (バウンディングボックス情報から行動認識)
        
        Args:
            detection: Person detection result (人物検出結果)
            frame_shape: Frame shape (height, width) (フレーム形状)
            
        Returns:
            ActionResult: Action recognition result (行動認識結果)
        """
        height, width = frame_shape
        x, y, w, h = detection.bbox
        
        # Analyze movement based on previous positions
        movement_confidence = self._analyze_movement(detection.center)
        
        # Analyze posture based on bounding box aspect ratio
        aspect_ratio = h / w if w > 0 else 1.0
        
        # Determine action based on aspect ratio and movement
        if aspect_ratio > 2.0:  # Tall and narrow - likely standing
            if movement_confidence > 0.5:
                action_type = ActionType.WALKING
                confidence = movement_confidence
            else:
                action_type = ActionType.STANDING
                confidence = 0.7
        elif aspect_ratio < 1.5:  # Wide and short - likely sitting
            action_type = ActionType.SITTING
            confidence = 0.6
        else:  # Medium aspect ratio
            if movement_confidence > 0.7:
                action_type = ActionType.WALKING
                confidence = movement_confidence
            else:
                action_type = ActionType.STANDING
                confidence = 0.5
        
        # Store current position for next frame
        self.previous_positions.append(detection.center)
        if len(self.previous_positions) > self.max_history:
            self.previous_positions.pop(0)
        
        return ActionResult(
            action_type=action_type,
            confidence=confidence,
            bbox=detection.bbox,
            timestamp=time.time(),
            details={
                'aspect_ratio': aspect_ratio,
                'movement_confidence': movement_confidence
            }
        )
    
    def _analyze_movement(self, current_center: Tuple[int, int]) -> float:
        """
        Analyze movement based on position history.
        (位置履歴に基づく動き解析)
        """
        if len(self.previous_positions) < 3:
            return 0.0
        
        # Calculate total movement over recent frames
        total_movement = 0.0
        for i in range(1, len(self.previous_positions)):
            prev_pos = self.previous_positions[i-1]
            curr_pos = self.previous_positions[i]
            
            distance = math.sqrt(
                (curr_pos[0] - prev_pos[0])**2 + 
                (curr_pos[1] - prev_pos[1])**2
            )
            total_movement += distance
        
        # Normalize movement (higher movement = more likely walking)
        movement_confidence = min(total_movement / 100.0, 1.0)
        return movement_confidence


class ActionRecognizer:
    """
    Unified action recognizer supporting multiple recognition methods.
    (複数の認識手法をサポートする統合行動認識器)
    """
    
    def __init__(self, use_pose: bool = True):
        """
        Initialize action recognizer.
        (行動認識器の初期化)
        
        Args:
            use_pose: Whether to use pose-based recognition (ポーズベース認識を使用するか)
        """
        self.use_pose = use_pose
        self.pose_recognizer = PoseActionRecognizer()
        self.bbox_recognizer = BBoxActionRecognizer()
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize action recognizer components.
        (行動認識器のコンポーネントを初期化)
        
        Returns:
            bool: True if initialization successful (初期化成功時True)
        """
        try:
            logger.info("Initializing action recognizer")
            logger.info("行動認識器を初期化中")
            
            # Initialize pose recognizer if enabled
            if self.use_pose:
                logger.info("Pose-based action recognition enabled")
                logger.info("ポーズベース行動認識が有効です")
            else:
                logger.info("Bounding box-based action recognition enabled")
                logger.info("バウンディングボックスベース行動認識が有効です")
            
            self.is_initialized = True
            logger.info("Action recognizer initialized successfully")
            logger.info("行動認識器の初期化が完了しました")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize action recognizer: {e}")
            logger.error(f"行動認識器の初期化に失敗しました: {e}")
            return False
        
    def recognize_actions(
        self, 
        detections: List[Detection], 
        poses: Optional[List[PersonPose]],
        frame_shape: Tuple[int, int]
    ) -> List[ActionResult]:
        """
        Recognize actions for multiple detections.
        (複数の検出に対する行動認識)
        
        Args:
            detections: List of person detections (人物検出結果のリスト)
            poses: List of person poses (人物ポーズのリスト)
            frame_shape: Frame shape (height, width) (フレーム形状)
            
        Returns:
            List[ActionResult]: List of action recognition results (行動認識結果のリスト)
        """
        results = []
        
        for i, detection in enumerate(detections):
            if self.use_pose and poses and i < len(poses):
                # Use pose-based recognition
                result = self.pose_recognizer.recognize_action(poses[i], frame_shape)
            else:
                # Use bbox-based recognition
                result = self.bbox_recognizer.recognize_action(detection, frame_shape)
            
            results.append(result)
        
        return results
    
    def visualize_actions(
        self, 
        frame: np.ndarray, 
        detections: List[Detection], 
        actions: List[ActionResult]
    ) -> np.ndarray:
        """
        Visualize action recognition results on frame.
        (フレームに行動認識結果を可視化)
        
        Args:
            frame: Input frame (入力フレーム)
            detections: Detection results (検出結果)
            actions: Action recognition results (行動認識結果)
            
        Returns:
            np.ndarray: Frame with action visualizations (行動可視化付きフレーム)
        """
        output_frame = frame.copy()
        
        # Color mapping for different actions
        action_colors = {
            ActionType.STANDING: (0, 255, 0),      # Green
            ActionType.SITTING: (0, 0, 255),       # Red
            ActionType.WALKING: (255, 0, 0),       # Blue
            ActionType.COMPUTER_INTERACTION: (255, 255, 0),  # Cyan
            ActionType.UNKNOWN: (128, 128, 128)    # Gray
        }
        
        for detection, action in zip(detections, actions):
            x, y, w, h = detection.bbox
            color = action_colors.get(action.action_type, (128, 128, 128))
            
            # Draw action label
            action_text = f"{action.action_type.value}: {action.confidence:.2f}"
            cv2.putText(
                output_frame, action_text, (x, y - 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )
            
            # Draw colored border based on action
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), color, 3)
        
        return output_frame