# API仕様書 - 研究室向けカメラベース監視システム
# API Documentation - Laboratory Camera-based Monitoring System

本文書では、研究室向けカメラベース監視システムの全モジュールにおける関数、クラス、メソッドの詳細な仕様を記載します。

## 目次 (Table of Contents)

1. [カメラモジュール (Camera Module)](#1-カメラモジュール-camera-module)
2. [検出モジュール (Detection Module)](#2-検出モジュール-detection-module)
3. [位置推定モジュール (Position Estimation Module)](#3-位置推定モジュール-position-estimation-module)
4. [行動認識モジュール (Action Recognition Module)](#4-行動認識モジュール-action-recognition-module)
5. [可視化モジュール (Visualization Module)](#5-可視化モジュール-visualization-module)
6. [システム統合モジュール (System Coordinator Module)](#6-システム統合モジュール-system-coordinator-module)
7. [設定管理モジュール (Configuration Module)](#7-設定管理モジュール-configuration-module)

---

## 1. カメラモジュール (Camera Module)
**ファイル**: `src/core/camera.py`

### 1.1 CameraManager クラス

カメラデバイスの管理とフレーム取得を行うメインクラス。

#### コンストラクタ
```python
def __init__(
    self,
    camera_id: int = 0,
    width: int = 640,
    height: int = 480,
    fps: int = 30,
) -> None:
```
**引数:**
- `camera_id` (int): カメラデバイスID (デフォルト: 0)
- `width` (int): フレーム幅 (デフォルト: 640)
- `height` (int): フレーム高さ (デフォルト: 480)
- `fps` (int): フレームレート (デフォルト: 30)

**戻り値:** なし

#### メソッド

##### initialize()
```python
def initialize(self) -> bool:
```
**説明:** カメラデバイスを初期化し、設定を適用します。

**引数:** なし

**戻り値:** 
- `bool`: 初期化成功時はTrue、失敗時はFalse

##### read_frame()
```python
def read_frame(self) -> Optional[np.ndarray]:
```
**説明:** カメラから1フレームを読み取ります。

**引数:** なし

**戻り値:**
- `Optional[np.ndarray]`: フレームデータ (BGRカラー画像) またはNone

##### get_frame_generator()
```python
def get_frame_generator(self) -> Generator[np.ndarray, None, None]:
```
**説明:** 連続的なフレーム読み取り用のジェネレータを返します。

**引数:** なし

**戻り値:**
- `Generator[np.ndarray, None, None]`: フレームデータのジェネレータ

##### get_async_frame_generator()
```python
async def get_async_frame_generator(self) -> AsyncGenerator[np.ndarray, None]:
```
**説明:** 非同期でのフレーム読み取り用のジェネレータを返します。

**引数:** なし

**戻り値:**
- `AsyncGenerator[np.ndarray, None]`: フレームデータの非同期ジェネレータ

##### get_camera_info()
```python
def get_camera_info(self) -> dict:
```
**説明:** カメラの設定情報を取得します。

**引数:** なし

**戻り値:**
- `dict`: カメラ情報辞書
  - `camera_id` (int): カメラID
  - `width` (int): フレーム幅
  - `height` (int): フレーム高さ
  - `fps` (int): フレームレート
  - `frame_count` (int): 処理済みフレーム数
  - `running_time` (float): 稼働時間
  - `is_running` (bool): 動作状態

##### get_stats()
```python
def get_stats(self) -> dict:
```
**説明:** カメラの統計情報を取得します。

**引数:** なし

**戻り値:**
- `dict`: 統計情報辞書
  - `total_frames` (int): 総フレーム数
  - `running_time` (float): 稼働時間
  - `actual_fps` (float): 実際のFPS
  - `target_fps` (int): 目標FPS

##### stop()
```python
def stop(self) -> None:
```
**説明:** カメラキャプチャを停止し、リソースを解放します。

**引数:** なし

**戻り値:** なし

### 1.2 MultiCameraManager クラス

複数のカメラを同時に管理するクラス。

#### コンストラクタ
```python
def __init__(self, camera_configs: list[dict]) -> None:
```
**引数:**
- `camera_configs` (list[dict]): カメラ設定辞書のリスト

**戻り値:** なし

#### メソッド

##### initialize_all()
```python
def initialize_all(self) -> bool:
```
**説明:** 全てのカメラを初期化します。

**引数:** なし

**戻り値:**
- `bool`: 少なくとも1台のカメラが初期化成功した場合はTrue

##### get_camera()
```python
def get_camera(self, camera_id: int) -> Optional[CameraManager]:
```
**説明:** 指定されたIDのカメラマネージャーを取得します。

**引数:**
- `camera_id` (int): カメラID

**戻り値:**
- `Optional[CameraManager]`: カメラマネージャーまたはNone

##### stop_all()
```python
def stop_all(self) -> None:
```
**説明:** 全てのカメラを停止します。

**引数:** なし

**戻り値:** なし

---

## 2. 検出モジュール (Detection Module)
**ファイル**: `src/core/detector.py`

### 2.1 データクラス

#### Detection
```python
@dataclass
class Detection:
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    class_id: int
    center: Tuple[int, int]
    timestamp: float
```

#### PersonPose
```python
@dataclass
class PersonPose:
    landmarks: List[Tuple[float, float]]  # x, y coordinates normalized
    visibility: List[float]  # visibility scores
    bbox: Tuple[int, int, int, int]  # estimated bounding box
    confidence: float
    timestamp: float
```

### 2.2 YOLODetector クラス

YOLO（You Only Look Once）を使用した人物検出クラス。

#### コンストラクタ
```python
def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
```
**引数:**
- `model_path` (str): YOLOモデルファイルのパス
- `confidence_threshold` (float): 検出信頼度の閾値

**戻り値:** なし

#### メソッド

##### initialize()
```python
def initialize(self) -> bool:
```
**説明:** YOLOモデルを読み込み初期化します。

**引数:** なし

**戻り値:**
- `bool`: 初期化成功時はTrue、失敗時はFalse

##### detect_persons()
```python
def detect_persons(self, frame: np.ndarray) -> List[Detection]:
```
**説明:** フレーム内の人物を検出します。

**引数:**
- `frame` (np.ndarray): 入力画像フレーム

**戻り値:**
- `List[Detection]`: 検出された人物のリスト

### 2.3 MediaPipeDetector クラス

MediaPipeを使用した姿勢推定付き人物検出クラス。

#### コンストラクタ
```python
def __init__(
    self,
    min_detection_confidence: float = 0.5,
    min_tracking_confidence: float = 0.5,
    model_complexity: int = 1
):
```
**引数:**
- `min_detection_confidence` (float): 最小検出信頼度
- `min_tracking_confidence` (float): 最小追跡信頼度
- `model_complexity` (int): モデル複雑度 (0, 1, 2)

**戻り値:** なし

#### メソッド

##### initialize()
```python
def initialize(self) -> bool:
```
**説明:** MediaPipe姿勢検出器を初期化します。

**引数:** なし

**戻り値:**
- `bool`: 初期化成功時はTrue、失敗時はFalse

##### detect_pose()
```python
def detect_pose(self, frame: np.ndarray) -> Optional[PersonPose]:
```
**説明:** フレーム内の人物姿勢を検出します。

**引数:**
- `frame` (np.ndarray): 入力画像フレーム

**戻り値:**
- `Optional[PersonPose]`: 姿勢情報またはNone

### 2.4 PersonDetector クラス

複数の検出方法を統合した人物検出クラス。

#### コンストラクタ
```python
def __init__(
    self,
    method: DetectionMethod = DetectionMethod.YOLO,
    yolo_model_path: str = "yolov8n.pt",
    confidence_threshold: float = 0.5
):
```
**引数:**
- `method` (DetectionMethod): 検出方法 (YOLO または MEDIAPIPE)
- `yolo_model_path` (str): YOLOモデルパス
- `confidence_threshold` (float): 信頼度閾値

**戻り値:** なし

#### メソッド

##### initialize()
```python
def initialize(self) -> bool:
```
**説明:** 選択された検出器を初期化します。

**引数:** なし

**戻り値:**
- `bool`: 初期化成功時はTrue、失敗時はFalse

##### detect()
```python
def detect(self, frame: np.ndarray) -> Dict[str, Any]:
```
**説明:** フレーム内の人物を検出します。

**引数:**
- `frame` (np.ndarray): 入力画像フレーム

**戻り値:**
- `Dict[str, Any]`: 検出結果辞書
  - `method` (str): 使用した検出方法
  - `detections` (List[Detection]): 検出結果リスト
  - `pose` (Optional[PersonPose]): 姿勢情報
  - `timestamp` (float): 処理時刻

##### visualize_detections()
```python
def visualize_detections(self, frame: np.ndarray, results: Dict[str, Any]) -> np.ndarray:
```
**説明:** 検出結果をフレーム上に可視化します。

**引数:**
- `frame` (np.ndarray): 入力画像フレーム
- `results` (Dict[str, Any]): 検出結果

**戻り値:**
- `np.ndarray`: 可視化済みフレーム

---

## 3. 位置推定モジュール (Position Estimation Module)
**ファイル**: `src/vision/position_estimator.py`

### 3.1 データクラス

#### RoomPosition
```python
@dataclass
class RoomPosition:
    x: float  # meters from left wall
    y: float  # meters from front wall
    confidence: float  # position confidence
    timestamp: float
    
    def distance_to(self, other: 'RoomPosition') -> float:
```

#### RoomDimensions
```python
@dataclass
class RoomDimensions:
    width: float = 4.0  # meters (width: 4m)
    height: float = 3.0  # meters (depth: 3m)
    camera_height: float = 2.5  # meters (camera height)
    
    def is_valid_position(self, position: RoomPosition) -> bool:
```

### 3.2 BBoxCenterEstimator クラス

バウンディングボックス中心を使用した簡単な位置推定クラス。

#### コンストラクタ
```python
def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
```
**引数:**
- `room_dimensions` (RoomDimensions): 部屋の寸法
- `frame_width` (int): フレーム幅
- `frame_height` (int): フレーム高さ

**戻り値:** なし

#### メソッド

##### estimate_position()
```python
def estimate_position(self, detection: Detection) -> RoomPosition:
```
**説明:** 検出結果から部屋内位置を推定します。

**引数:**
- `detection` (Detection): 人物検出結果

**戻り値:**
- `RoomPosition`: 推定された部屋内位置

### 3.3 PerspectiveMappingEstimator クラス

透視変換を使用した位置推定クラス。

#### コンストラクタ
```python
def __init__(self, room_dimensions: RoomDimensions):
```
**引数:**
- `room_dimensions` (RoomDimensions): 部屋の寸法

**戻り値:** なし

#### メソッド

##### calibrate()
```python
def calibrate(self, image_corners: np.ndarray) -> bool:
```
**説明:** 画像のコーナーポイントを使用して透視変換を較正します。

**引数:**
- `image_corners` (np.ndarray): 画像座標での4つのコーナーポイント (4x2配列)

**戻り値:**
- `bool`: 較正成功時はTrue、失敗時はFalse

##### use_default_calibration()
```python
def use_default_calibration(self) -> bool:
```
**説明:** テスト用のデフォルト較正を使用します。

**引数:** なし

**戻り値:**
- `bool`: 較正成功時はTrue、失敗時はFalse

##### estimate_position()
```python
def estimate_position(self, detection: Detection) -> Optional[RoomPosition]:
```
**説明:** 透視変換を使用して部屋内位置を推定します。

**引数:**
- `detection` (Detection): 人物検出結果

**戻り値:**
- `Optional[RoomPosition]`: 推定された部屋内位置またはNone

### 3.4 DepthEstimationEstimator クラス

人物サイズからの深度推定を使用した位置推定クラス。

#### コンストラクタ
```python
def __init__(self, room_dimensions: RoomDimensions, frame_width: int, frame_height: int):
```
**引数:**
- `room_dimensions` (RoomDimensions): 部屋の寸法
- `frame_width` (int): フレーム幅
- `frame_height` (int): フレーム高さ

**戻り値:** なし

#### メソッド

##### estimate_position()
```python
def estimate_position(self, detection: Detection) -> RoomPosition:
```
**説明:** 深度推定を使用して部屋内位置を推定します。

**引数:**
- `detection` (Detection): 人物検出結果

**戻り値:**
- `RoomPosition`: 推定された部屋内位置

### 3.5 PositionEstimator クラス

複数の位置推定方法を統合したクラス。

#### コンストラクタ
```python
def __init__(
    self,
    method: PositionMethod = PositionMethod.BBOX_CENTER,
    room_dimensions: Optional[RoomDimensions] = None,
    frame_width: int = 640,
    frame_height: int = 480
):
```
**引数:**
- `method` (PositionMethod): 位置推定方法
- `room_dimensions` (Optional[RoomDimensions]): 部屋の寸法
- `frame_width` (int): フレーム幅
- `frame_height` (int): フレーム高さ

**戻り値:** なし

#### メソッド

##### estimate_positions()
```python
def estimate_positions(self, detections: List[Detection]) -> List[RoomPosition]:
```
**説明:** 複数の検出結果に対して位置推定を実行します。

**引数:**
- `detections` (List[Detection]): 人物検出結果のリスト

**戻り値:**
- `List[RoomPosition]`: 推定された部屋内位置のリスト

##### visualize_positions()
```python
def visualize_positions(
    self, 
    frame: np.ndarray, 
    detections: List[Detection], 
    positions: List[RoomPosition]
) -> np.ndarray:
```
**説明:** 推定位置をフレーム上に可視化します。

**引数:**
- `frame` (np.ndarray): 入力画像フレーム
- `detections` (List[Detection]): 検出結果
- `positions` (List[RoomPosition]): 推定位置

**戻り値:**
- `np.ndarray`: 可視化済みフレーム

##### get_room_occupancy_map()
```python
def get_room_occupancy_map(self, positions: List[RoomPosition]) -> np.ndarray:
```
**説明:** 位置情報から部屋の占有マップを生成します。

**引数:**
- `positions` (List[RoomPosition]): 部屋内位置のリスト

**戻り値:**
- `np.ndarray`: 占有マップ (10cm解像度)

---

## 4. 行動認識モジュール (Action Recognition Module)
**ファイル**: `src/vision/action_recognizer.py`

### 4.1 データクラス

#### ActionResult
```python
@dataclass
class ActionResult:
    action_type: ActionType
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    timestamp: float
    details: Dict[str, Any]  # Additional action-specific details
```

### 4.2 PoseActionRecognizer クラス

姿勢ランドマークを使用した行動認識クラス。

#### コンストラクタ
```python
def __init__(self):
```
**引数:** なし

**戻り値:** なし

#### メソッド

##### recognize_action()
```python
def recognize_action(self, pose: PersonPose, frame_shape: Tuple[int, int]) -> ActionResult:
```
**説明:** 姿勢ランドマークから行動を認識します。

**引数:**
- `pose` (PersonPose): 人物姿勢情報
- `frame_shape` (Tuple[int, int]): フレーム形状 (高さ, 幅)

**戻り値:**
- `ActionResult`: 行動認識結果

### 4.3 BBoxActionRecognizer クラス

バウンディングボックス情報を使用した行動認識クラス。

#### コンストラクタ
```python
def __init__(self):
```
**引数:** なし

**戻り値:** なし

#### メソッド

##### recognize_action()
```python
def recognize_action(self, detection: Detection, frame_shape: Tuple[int, int]) -> ActionResult:
```
**説明:** バウンディングボックス情報から行動を認識します。

**引数:**
- `detection` (Detection): 人物検出結果
- `frame_shape` (Tuple[int, int]): フレーム形状 (高さ, 幅)

**戻り値:**
- `ActionResult`: 行動認識結果

### 4.4 ActionRecognizer クラス

複数の認識方法を統合した行動認識クラス。

#### コンストラクタ
```python
def __init__(self, use_pose: bool = True):
```
**引数:**
- `use_pose` (bool): 姿勢ベース認識を使用するか

**戻り値:** なし

#### メソッド

##### recognize_actions()
```python
def recognize_actions(
    self, 
    detections: List[Detection], 
    poses: Optional[List[PersonPose]],
    frame_shape: Tuple[int, int]
) -> List[ActionResult]:
```
**説明:** 複数の検出結果に対して行動認識を実行します。

**引数:**
- `detections` (List[Detection]): 人物検出結果のリスト
- `poses` (Optional[List[PersonPose]]): 人物姿勢のリスト
- `frame_shape` (Tuple[int, int]): フレーム形状

**戻り値:**
- `List[ActionResult]`: 行動認識結果のリスト

##### visualize_actions()
```python
def visualize_actions(
    self, 
    frame: np.ndarray, 
    detections: List[Detection], 
    actions: List[ActionResult]
) -> np.ndarray:
```
**説明:** 行動認識結果をフレーム上に可視化します。

**引数:**
- `frame` (np.ndarray): 入力画像フレーム
- `detections` (List[Detection]): 検出結果
- `actions` (List[ActionResult]): 行動認識結果

**戻り値:**
- `np.ndarray`: 可視化済みフレーム

---

## 5. 可視化モジュール (Visualization Module)
**ファイル**: `src/visualization/display.py`

### 5.1 MonitoringDisplay クラス

監視システムの可視化表示を管理するメインクラス。

#### コンストラクタ
```python
def __init__(self, config: DisplayConfig) -> None:
```
**引数:**
- `config` (DisplayConfig): 表示設定

**戻り値:** なし

#### メソッド

##### initialize()
```python
def initialize(self) -> bool:
```
**説明:** 表示システムを初期化し、ウィンドウを作成します。

**引数:** なし

**戻り値:** `bool` - 初期化成功時True

##### render_frame()
```python
def render_frame(
    self,
    frame: np.ndarray,
    detections: List[Detection],
    positions: List[RoomPosition],
    actions: List[ActionResult],
    room_width: float = 4.0,
    room_height: float = 3.0,
    additional_info: Optional[Dict[str, Any]] = None
) -> Optional[np.ndarray]:
```
**説明:** フレームに可視化オーバーレイを描画します。

**引数:**
- `frame` (np.ndarray): 入力フレーム
- `detections` (List[Detection]): 検出結果リスト
- `positions` (List[RoomPosition]): 位置推定結果リスト
- `actions` (List[ActionResult]): 行動認識結果リスト
- `room_width` (float): 部屋の幅[m] (デフォルト: 4.0)
- `room_height` (float): 部屋の高さ[m] (デフォルト: 3.0)
- `additional_info` (Optional[Dict[str, Any]]): 追加表示情報

**戻り値:** `Optional[np.ndarray]` - レンダリング済みフレームまたはNone

##### cleanup()
```python
def cleanup(self) -> None:
```
**説明:** 表示リソースをクリーンアップします。

**引数:** なし

**戻り値:** なし

### 5.2 DisplayConfig クラス

表示設定を管理するデータクラス。

#### 属性
- `mode` (DisplayMode): 表示モード (NONE/WINDOW/HEADLESS)
- `window_name` (str): ウィンドウ名
- `window_width` (int): ウィンドウ幅
- `window_height` (int): ウィンドウ高さ
- `show_fps` (bool): FPS表示フラグ
- `show_detection_count` (bool): 検出数表示フラグ
- `show_position_info` (bool): 位置情報表示フラグ
- `show_action_info` (bool): 行動情報表示フラグ
- `bbox_thickness` (int): バウンディングボックス線の太さ
- `text_scale` (float): テキストスケール
- `text_thickness` (int): テキスト線の太さ

### 5.3 DisplayMode enum

表示モードを定義する列挙型。

#### 値
- `NONE`: 表示なし
- `WINDOW`: ウィンドウ表示
- `HEADLESS`: ヘッドレス表示

### 5.4 ユーティリティ関数

#### create_display_config()
```python
def create_display_config(
    mode: str = "none",
    window_name: str = "Laboratory Monitoring System",
    show_fps: bool = True,
    show_detection_count: bool = True,
    show_position_info: bool = True,
    show_action_info: bool = True
) -> DisplayConfig:
```
**説明:** 表示設定を作成します。

**引数:**
- `mode` (str): 表示モード ("none", "window", "headless")
- `window_name` (str): ウィンドウ名
- `show_fps` (bool): FPS表示フラグ
- `show_detection_count` (bool): 検出数表示フラグ
- `show_position_info` (bool): 位置情報表示フラグ
- `show_action_info` (bool): 行動情報表示フラグ

**戻り値:** `DisplayConfig` - 表示設定

---

## 6. システム統合モジュール (System Coordinator Module)
**ファイル**: `src/core/coordinator.py`

### 6.1 MonitoringCoordinator クラス

全監視コンポーネントを統合するメインコーディネータクラス。

#### コンストラクタ
```python
def __init__(
    self,
    camera_id: int = 0,
    config_path: Optional[Path] = None,
    detection_method: DetectionMethod = DetectionMethod.YOLO,
    position_method: PositionMethod = PositionMethod.BBOX_CENTER,
    display_config: Optional[DisplayConfig] = None
):
```
**引数:**
- `camera_id` (int): カメラデバイスID
- `config_path` (Optional[Path]): 設定ファイルパス
- `detection_method` (DetectionMethod): 人物検出方法
- `position_method` (PositionMethod): 位置推定方法
- `display_config` (Optional[DisplayConfig]): 表示設定

**戻り値:** なし

#### メソッド

##### initialize()
```python
async def initialize(self) -> bool:
```
**説明:** 全システムコンポーネントを初期化します。

**引数:** なし

**戻り値:**
- `bool`: 初期化成功時はTrue、失敗時はFalse

##### start_monitoring()
```python
async def start_monitoring(self) -> None:
```
**説明:** メイン監視ループを開始します。

**引数:** なし

**戻り値:** なし

##### stop_monitoring()
```python
async def stop_monitoring(self) -> None:
```
**説明:** 監視システムを停止します。

**引数:** なし

**戻り値:** なし

##### get_system_stats()
```python
def get_system_stats(self) -> Dict[str, Any]:
```
**説明:** 現在のシステム統計情報を取得します。

**引数:** なし

**戻り値:**
- `Dict[str, Any]`: システム統計情報
  - `is_running` (bool): 動作状態
  - `frame_count` (int): 処理済みフレーム数
  - `elapsed_time` (float): 経過時間
  - `avg_fps` (float): 平均FPS
  - `detection_method` (str): 検出方法
  - `position_method` (str): 位置推定方法
  - `room_dimensions` (dict): 部屋の寸法
  - `camera` (dict): カメラ統計情報

---

## 7. 設定管理モジュール (Configuration Module)
**ファイル**: `src/utils/config.py`

### 7.1 設定データクラス

#### CameraConfig
```python
@dataclass
class CameraConfig:
    camera_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
```

#### RoomConfig
```python
@dataclass
class RoomConfig:
    width: float = 4.0  # meters
    height: float = 3.0  # meters
    camera_height: float = 2.5  # meters
```

#### DetectionConfig
```python
@dataclass
class DetectionConfig:
    method: str = "yolo"  # "yolo" or "mediapipe"
    confidence_threshold: float = 0.5
    yolo_model_path: str = "yolov8n.pt"
```

#### PositionConfig
```python
@dataclass
class PositionConfig:
    method: str = "bbox_center"  # "bbox_center", "perspective_mapping", "depth_estimation"
    calibration_points: Optional[list] = None  # For perspective mapping
```

#### ActionConfig
```python
@dataclass
class ActionConfig:
    use_pose: bool = True
    confidence_threshold: float = 0.3
```

#### DisplayConfig
```python
@dataclass
class DisplayConfig:
    mode: str = "none"  # "none", "window", "headless"
    window_name: str = "Laboratory Monitoring System"
    show_fps: bool = True
    show_detection_count: bool = True
    show_position_info: bool = True
    show_action_info: bool = True
```

#### SystemConfig
```python
@dataclass
class SystemConfig:
    display_enabled: bool = True
    save_results: bool = False
    output_directory: str = "output"
    log_level: str = "INFO"
```

### 7.2 Config クラス

メイン設定管理クラス。

#### コンストラクタ
```python
def __init__(
    self,
    camera: CameraConfig,
    room: RoomConfig,
    detection: DetectionConfig,
    position: PositionConfig,
    action: ActionConfig,
    display: DisplayConfig,
    system: SystemConfig
):
```
**引数:**
- `camera` (CameraConfig): カメラ設定
- `room` (RoomConfig): 部屋設定
- `detection` (DetectionConfig): 検出設定
- `position` (PositionConfig): 位置推定設定
- `action` (ActionConfig): 行動認識設定
- `display` (DisplayConfig): 表示設定
- `system` (SystemConfig): システム設定

**戻り値:** なし

#### クラスメソッド

##### from_file()
```python
@classmethod
def from_file(cls, config_path: Path) -> "Config":
```
**説明:** ファイルから設定を読み込みます。

**引数:**
- `config_path` (Path): 設定ファイルのパス

**戻り値:**
- `Config`: 設定インスタンス

##### from_dict()
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Config":
```
**説明:** 辞書から設定を作成します。

**引数:**
- `data` (Dict[str, Any]): 設定データ辞書

**戻り値:**
- `Config`: 設定インスタンス

##### default()
```python
@classmethod
def default(cls) -> "Config":
```
**説明:** デフォルト設定を作成します。

**引数:** なし

**戻り値:**
- `Config`: デフォルト設定インスタンス

#### インスタンスメソッド

##### to_dict()
```python
def to_dict(self) -> Dict[str, Any]:
```
**説明:** 設定を辞書に変換します。

**引数:** なし

**戻り値:**
- `Dict[str, Any]`: 設定辞書

##### save_to_file()
```python
def save_to_file(self, config_path: Path) -> bool:
```
**説明:** 設定をファイルに保存します。

**引数:**
- `config_path` (Path): 保存先パス

**戻り値:**
- `bool`: 保存成功時はTrue、失敗時はFalse

### 6.3 ユーティリティ関数

#### create_sample_config()
```python
def create_sample_config() -> Config:
```
**説明:** テスト用サンプル設定を作成します。

**引数:** なし

**戻り値:**
- `Config`: サンプル設定インスタンス

---

## 使用例 (Usage Examples)

### 基本的な使用例
```python
from src.core.coordinator import MonitoringCoordinator
from src.core.detector import DetectionMethod
from src.vision.position_estimator import PositionMethod

# システム初期化
coordinator = MonitoringCoordinator(
    camera_id=0,
    detection_method=DetectionMethod.YOLO,
    position_method=PositionMethod.BBOX_CENTER
)

# 初期化と実行
await coordinator.initialize()
await coordinator.start_monitoring()
```

### 設定ファイルを使用した例
```python
from pathlib import Path
from src.utils.config import Config
from src.core.coordinator import MonitoringCoordinator

# 設定読み込み
config = Config.from_file(Path("config.yaml"))

# システム初期化
coordinator = MonitoringCoordinator(
    camera_id=config.camera.camera_id,
    detection_method=DetectionMethod(config.detection.method),
    position_method=PositionMethod(config.position.method)
)
```

---

本API仕様書は研究室向けカメラベース監視システムの全機能を網羅しており、各モジュールの詳細な使用方法を提供しています。実装や拡張の際の参考資料としてご活用ください。