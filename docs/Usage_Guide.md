# 使用ガイド - 研究室向けカメラベース監視システム
# Usage Guide - Laboratory Camera-based Monitoring System

このガイドでは、研究室向けカメラベース監視システムの使用方法を詳しく説明します。

## 目次

1. [システム要件](#1-システム要件)
2. [インストールと設定](#2-インストールと設定)
3. [基本的な使用方法](#3-基本的な使用方法)
4. [設定ファイルの使用](#4-設定ファイルの使用)
5. [各モジュールの個別使用](#5-各モジュールの個別使用)
6. [トラブルシューティング](#6-トラブルシューティング)

---

## 1. システム要件

### ハードウェア要件
- **CPU**: Intel i5 以上 (GPU使用推奨)
- **RAM**: 8GB 以上
- **カメラ**: USB Webカメラ (1080p推奨)
- **ストレージ**: 5GB 以上の空き容量

### ソフトウェア要件
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **Anaconda**: 2023.03+ または Miniconda 23.3.1+
- **Python**: 3.11+ (Anaconda環境内)

### 対応カメラ
- USB Webカメラ (UVC対応)
- 内蔵カメラ
- IP カメラ (RTSP対応)

---

## 2. インストールと設定

### 2.1 リポジトリのクローン
```bash
git clone <repository-url>
cd PBL_test
```

### 2.2 Anaconda環境での実行（推奨）

#### ステップ1: Anaconda環境の作成と有効化
```bash
# 新しい環境を作成
conda create -n lab_monitoring python=3.11

# 環境をアクティベート
conda activate lab_monitoring
```

#### ステップ2: 基本ライブラリのインストール
```bash
# Condaでインストール可能な基本ライブラリ
conda install -c conda-forge opencv numpy scipy matplotlib pillow pyyaml

# Condaでインストール可能な科学計算ライブラリ
conda install -c conda-forge pandas scikit-learn scikit-image
```

#### ステップ3: PyTorchのインストール
```bash
# GPU使用時 (CUDA 11.8対応)
conda install pytorch torchvision pytorch-cuda=11.8 -c pytorch -c nvidia

# GPU使用時 (CUDA 12.1対応)
conda install pytorch torchvision pytorch-cuda=12.1 -c pytorch -c nvidia

# CPU使用時
conda install pytorch torchvision cpuonly -c pytorch
```

#### ステップ4: その他の専用ライブラリのインストール
```bash
# pipでインストールが必要なライブラリ
pip install ultralytics mediapipe transformers timm
pip install flask fastapi uvicorn click loguru
pip install pytest pytest-cov black ruff

# または一括インストール
pip install -r requirements-conda.txt
```

#### ステップ5: システム実行
```bash
# 環境がアクティベートされていることを確認
conda activate lab_monitoring

# システム実行
python main.py
```

#### 環境の管理
```bash
# 環境一覧の確認
conda env list

# 環境の削除
conda env remove -n lab_monitoring

# 環境のエクスポート
conda env export > environment.yml

# 環境のインポート
conda env create -f environment.yml
```

### 2.3 環境ファイルを使用したインストール（推奨）

#### environment.ymlを使用した環境作成
```yaml
# environment.yml ファイルの例
name: lab_monitoring
channels:
  - conda-forge
  - pytorch
  - nvidia
dependencies:
  - python=3.11
  - opencv
  - numpy
  - scipy
  - matplotlib
  - pillow
  - pandas
  - scikit-learn
  - scikit-image
  - pyyaml
  - pytorch
  - torchvision
  - pytorch-cuda=11.8
  - pip
  - pip:
    - ultralytics>=8.0.0
    - mediapipe>=0.10.0
    - transformers>=4.30.0
    - timm>=0.9.0
    - flask>=3.0.0
    - fastapi>=0.100.0
    - uvicorn>=0.20.0
    - click>=8.0.0
    - loguru>=0.7.0
    - pytest>=7.4.0
    - black>=23.0.0
    - ruff>=0.1.0
```

```bash
# environment.ymlから環境を作成
conda env create -f environment.yml

# 環境をアクティベート
conda activate lab_monitoring

# システム実行
python main.py
```

### 2.4 ローカル環境での実行
```bash
# 依存関係のインストール
pip install -r requirements.txt

# システム実行
python main.py
```

---

## 3. 基本的な使用方法

### 3.1 標準実行
```bash
# Anaconda環境をアクティベート
conda activate lab_monitoring

# デフォルト設定で実行（表示なし）
python main.py

# ウィンドウ表示で実行
python main.py --display window

# ウィンドウ表示でFPSと詳細情報を表示
python main.py --display window --show-fps --show-info

# カメラIDを指定してウィンドウ表示
python main.py --camera-id 1 --display window

# デバッグモードで実行
python main.py --debug --display window
```

### 3.2 コマンドラインオプション
```bash
python main.py [OPTIONS]

オプション:
  --camera-id INTEGER     カメラデバイスID (デフォルト: 0)
  --debug                 デバッグモードを有効化
  --config PATH          設定ファイルのパス
  --display [none|window|headless]  表示モード (デフォルト: none)
  --show-fps             FPSカウンターを表示
  --show-info            検出・位置情報を表示
  --help                 ヘルプメッセージを表示
```

### 3.3 実行中の操作

#### コマンドライン操作
- **Ctrl+C**: システム終了

#### ディスプレイウィンドウ操作（--display window時）
- **ESCキー**: ウィンドウを閉じてシステム終了
- **ウィンドウ×ボタン**: ウィンドウを閉じてシステム終了

#### 表示される情報
- **バウンディングボックス**: 検出された人物の周囲に表示
- **信頼度**: 検出の信頼度（0.0-1.0）
- **位置情報**: 部屋内での推定位置（x, y座標とメートル単位の距離）
- **行動情報**: 検出された行動（立つ/座る/コンピューター操作/歩行など）
- **FPS**: フレームレート（--show-fps使用時）
- **検出数**: 現在のフレームでの検出数
- **部屋レイアウト**: 右下に表示される部屋の俯瞰図と位置マーカー

---

## 4. 設定ファイルの使用

### 4.1 設定ファイルの作成

#### YAML形式の設定例（config.yaml）
```yaml
# カメラ設定
camera:
  camera_id: 0
  width: 640
  height: 480
  fps: 30

# 部屋設定
room:
  width: 4.0      # メートル
  height: 3.0     # メートル
  camera_height: 2.5

# 検出設定
detection:
  method: "yolo"  # "yolo" または "mediapipe"
  confidence_threshold: 0.6
  yolo_model_path: "yolov8n.pt"

# 位置推定設定
position:
  method: "bbox_center"  # "bbox_center", "perspective_mapping", "depth_estimation"
  calibration_points: null

# 行動認識設定
action:
  use_pose: true
  confidence_threshold: 0.3

# 表示設定
display:
  mode: "window"  # "none", "window", "headless"
  window_name: "Laboratory Monitoring System"
  show_fps: true
  show_detection_count: true
  show_position_info: true
  show_action_info: true

# システム設定
system:
  display_enabled: true
  save_results: false
  output_directory: "output"
  log_level: "INFO"
```

#### JSON形式の設定例（config.json）
```json
{
  "camera": {
    "camera_id": 0,
    "width": 640,
    "height": 480,
    "fps": 30
  },
  "room": {
    "width": 4.0,
    "height": 3.0,
    "camera_height": 2.5
  },
  "detection": {
    "method": "yolo",
    "confidence_threshold": 0.6,
    "yolo_model_path": "yolov8n.pt"
  },
  "position": {
    "method": "bbox_center",
    "calibration_points": null
  },
  "action": {
    "use_pose": true,
    "confidence_threshold": 0.3
  },
  "display": {
    "mode": "window",
    "window_name": "Laboratory Monitoring System",
    "show_fps": true,
    "show_detection_count": true,
    "show_position_info": true,
    "show_action_info": true
  },
  "system": {
    "display_enabled": true,
    "save_results": false,
    "output_directory": "output",
    "log_level": "INFO"
  }
}
```

### 4.2 設定ファイルを使用した実行
```bash
# YAML設定ファイルを使用
python main.py --config config.yaml

# JSON設定ファイルを使用
python main.py --config config.json
```

---

## 5. 各モジュールの個別使用

### 5.1 カメラモジュールの単独使用
```python
from src.camera.manager import CameraManager

# カメラ初期化
camera = CameraManager(camera_id=0, width=640, height=480, fps=30)
camera.initialize()

# フレーム取得
frame = camera.read_frame()
if frame is not None:
    # フレーム処理
    pass

# リソース解放
camera.stop()
```

#### 5.1a マルチカメラ使用
```python
from src.camera.multi_camera import MultiCameraManager

# 複数カメラの設定
camera_configs = [
    {'camera_id': 0, 'width': 640, 'height': 480, 'fps': 30},
    {'camera_id': 1, 'width': 640, 'height': 480, 'fps': 30}
]

# マルチカメラマネージャー初期化
multi_camera = MultiCameraManager(camera_configs)
multi_camera.initialize_all()

# 特定のカメラからフレーム取得
camera_0 = multi_camera.get_camera(0)
if camera_0:
    frame = camera_0.read_frame()
```

### 5.2 人物検出の単独使用
```python
from src.detection.detector import PersonDetector, DetectionMethod

# YOLO検出器
detector = PersonDetector(method=DetectionMethod.YOLO)
detector.initialize()

# 検出実行
results = detector.detect(frame)
detections = results['detections']

# MediaPipe検出器
detector_mp = PersonDetector(method=DetectionMethod.MEDIAPIPE)
detector_mp.initialize()
results_mp = detector_mp.detect(frame)
```

#### 5.2a YOLO特化検出器の使用
```python
from src.detection.yolo import YOLODetector

# YOLO特化検出器
yolo_detector = YOLODetector(model_path="yolov8n.pt", confidence_threshold=0.6)
yolo_detector.initialize()

# 人物検出
detections = yolo_detector.detect_persons(frame)
```

#### 5.2b MediaPipe特化検出器の使用
```python
from src.detection.mediapipe import MediaPipeDetector

# MediaPipe特化検出器
mp_detector = MediaPipeDetector(min_detection_confidence=0.5)
mp_detector.initialize()

# 姿勢検出
pose = mp_detector.detect_pose(frame)
```

### 5.3 位置推定の単独使用
```python
from src.position_estimation.estimator import PositionEstimator, PositionMethod, RoomDimensions

# 部屋設定
room = RoomDimensions(width=4.0, height=3.0, camera_height=2.5)

# 位置推定器初期化
estimator = PositionEstimator(
    method=PositionMethod.BBOX_CENTER,
    room_dimensions=room,
    frame_width=640,
    frame_height=480
)

# 位置推定実行
positions = estimator.estimate_positions(detections)
```

#### 5.3a 位置推定マネージャーの使用
```python
from src.position_estimation.manager import PositionEstimationManager

# 位置推定マネージャー初期化
manager = PositionEstimationManager(
    method=PositionMethod.PERSPECTIVE_MAPPING,
    room_dimensions=room,
    frame_width=640,
    frame_height=480
)

# 位置推定実行
positions = manager.estimate_positions(detections, frame)

# 手法の変更
manager.change_method(PositionMethod.DEPTH_ESTIMATION)
```

#### 5.3b 透視変換位置推定の使用
```python
from src.position_estimation.perspective import PerspectiveMappingEstimator

# 透視変換推定器
perspective_estimator = PerspectiveMappingEstimator(room_dimensions=room)

# 較正用コーナーポイントを設定
corners = np.array([[0, 0], [640, 0], [640, 480], [0, 480]])
perspective_estimator.calibrate(corners)

# 位置推定
position = perspective_estimator.estimate_position(detection)
```

### 5.4 行動認識の単独使用
```python
from src.action_recognition.recognizer import ActionRecognizer

# 行動認識器初期化
recognizer = ActionRecognizer(use_pose=True)

# 行動認識実行
actions = recognizer.recognize_actions(detections, poses, (480, 640))
```

#### 5.4a 姿勢ベース行動認識の使用
```python
from src.action_recognition.pose import PoseActionRecognizer

# 姿勢ベース認識器
pose_recognizer = PoseActionRecognizer()

# 姿勢情報から行動認識
action_result = pose_recognizer.recognize_action(pose, (480, 640))
```

#### 5.4b バウンディングボックスベース行動認識の使用
```python
from src.action_recognition.bbox import BBoxActionRecognizer

# バウンディングボックスベース認識器
bbox_recognizer = BBoxActionRecognizer()

# 検出情報から行動認識
action_result = bbox_recognizer.recognize_action(detection, (480, 640))
```

---

## 6. トラブルシューティング

### 6.1 よくある問題

#### カメラが認識されない
```bash
# カメラデバイスの確認 (Linux)
ls /dev/video*

# カメラテスト
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera:', cap.isOpened())"
```

**解決方法:**
- カメラIDを変更: `--camera-id 1`
- USB接続を確認
- 他のアプリケーションでカメラが使用されていないか確認

#### YOLOモデルのダウンロードエラー
```bash
# 手動でモデルダウンロード
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

**解決方法:**
- インターネット接続を確認
- プロキシ設定が必要な場合は環境変数を設定
- より軽量なモデルを使用: `yolov8n.pt`

#### メモリ不足エラー
**解決方法:**
- フレームサイズを小さくする: `width=320, height=240`
- 処理頻度を下げる
- GPUメモリを確認（GPU使用時）

#### パフォーマンスが低い
**最適化のヒント:**
- GPU使用を有効化
- フレームレートを下げる: `fps=15`
- 信頼度閾値を上げる: `confidence_threshold=0.7`
- より軽量な検出方法を使用

### 6.2 ログレベルの調整
```python
# デバッグ情報を詳細表示
python main.py --debug

# 設定ファイルでログレベル調整
system:
  log_level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

### 6.3 Anaconda環境関連の問題

#### 環境が見つからない・アクティベートできない
```bash
# 環境一覧確認
conda env list

# 環境の再作成
conda env remove -n lab_monitoring
conda create -n lab_monitoring python=3.11
conda activate lab_monitoring

# 依存関係の再インストール
conda install -c conda-forge opencv numpy scipy matplotlib pillow
pip install -r requirements-conda.txt
```

#### パッケージのインストールエラー
```bash
# conda-forgeチャンネルを優先して使用
conda config --add channels conda-forge

# pipのアップグレード
python -m pip install --upgrade pip

# キャッシュクリア
conda clean --all
pip cache purge

# 個別にパッケージをインストール
conda install opencv -c conda-forge
conda install pytorch torchvision -c pytorch
```

#### GPU関連の問題
```bash
# CUDA環境の確認
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"

# CUDA対応PyTorchのインストール
conda install pytorch torchvision pytorch-cuda=11.8 -c pytorch -c nvidia

# CPU版PyTorchに変更（GPUが使用できない場合）
conda install pytorch torchvision cpuonly -c pytorch
```

### 6.4 パフォーマンス最適化

#### システム要件別推奨設定

**低スペックPC用設定:**
```yaml
camera:
  width: 320
  height: 240
  fps: 15
detection:
  confidence_threshold: 0.7
```

**高スペックPC用設定:**
```yaml
camera:
  width: 1280
  height: 720
  fps: 30
detection:
  confidence_threshold: 0.5
position:
  method: "perspective_mapping"
```

### 5.5 統合システムの使用
```python
from src.monitoring.coordinator import MonitoringCoordinator
from src.detection.detector import DetectionMethod
from src.position_estimation.estimator import PositionMethod
from src.monitoring.display.display import DisplayConfig

# システムコーディネーター初期化
coordinator = MonitoringCoordinator(
    camera_id=0,
    detection_method=DetectionMethod.YOLO,
    position_method=PositionMethod.BBOX_CENTER,
    display_config=DisplayConfig(mode="window")
)

# システム初期化と実行
await coordinator.initialize()
await coordinator.start_monitoring()
```

### 5.6 設定ファイルを使用した統合システム
```python
from pathlib import Path
from src.config.config import Config
from src.monitoring.coordinator import MonitoringCoordinator

# 設定読み込み
config = Config.from_file(Path("config.yaml"))

# 設定を使用したコーディネーター初期化
coordinator = MonitoringCoordinator(
    camera_id=config.camera.camera_id,
    detection_method=DetectionMethod(config.detection.method),
    position_method=PositionMethod(config.position.method),
    display_config=config.display
)

# システム実行
await coordinator.initialize()
await coordinator.start_monitoring()
```

### 5.7 データ保存と処理
```python
from src.storage.storage import StorageManager
from src.storage.processor import DataProcessor

# データ保存マネージャー
storage_manager = StorageManager(storage_type="local")

# データ処理器
data_processor = DataProcessor()

# 検出結果の保存
storage_manager.save_detection_results(detections, timestamp)

# 位置情報の保存
storage_manager.save_position_data(positions, timestamp)

# データ処理と統計
processed_data = data_processor.process_session_data(session_data)
```


### 5.9 オブジェクト追跡の使用
```python
from src.monitoring.tracker import ObjectTracker

# オブジェクト追跡器初期化
tracker = ObjectTracker(max_disappeared=30, max_distance=100)

# 検出結果を追跡
tracked_objects = tracker.update(detections)

# 追跡統計の取得
tracking_stats = tracker.get_statistics()
```

---

## 付録

### A. サポートされている検出方法
1. **YOLO (You Only Look Once)** - `src/detection/yolo/`
   - 高速・高精度
   - GPU推奨
   - モデルサイズ: yolov8n.pt (6MB) ～ yolov8x.pt (136MB)

2. **MediaPipe** - `src/detection/mediapipe/`
   - CPU最適化
   - 姿勢情報付き
   - リアルタイム処理

### B. サポートされている位置推定方法
1. **bbox_center** - `src/position_estimation/estimator.py`: 最も軽量、基本的な精度
2. **perspective_mapping** - `src/position_estimation/perspective/`: 高精度、要較正
3. **depth_estimation** - `src/position_estimation/ai_models/`: 中程度精度、設定不要
4. **mediapipe_pose** - `src/position_estimation/pose/`: 姿勢ベース、中程度精度
5. **midas_depth** - `src/position_estimation/ai_models/midas/`: AI深度推定、高精度
6. **dpt_depth** - `src/position_estimation/ai_models/dpt/`: 最新AI深度推定、最高精度

### C. 認識可能な行動
- **Standing** (立っている) - `src/action_recognition/pose/` 及び `src/action_recognition/bbox/`
- **Sitting** (座っている) - `src/action_recognition/pose/` 及び `src/action_recognition/bbox/`
- **Walking** (歩いている) - `src/action_recognition/bbox/` 及び `src/monitoring/tracker.py`
- **Computer Interaction** (コンピュータ操作) - `src/action_recognition/pose/`
- **Unknown** (不明) - デフォルト状態

### D. 出力形式
- **リアルタイム表示**: OpenCVウィンドウ - `src/monitoring/display/display.py`
- **画像保存**: JPEG形式 - `src/storage/local/`
- **データ出力**: JSON形式 - `src/storage/processor.py`
- **統計情報**: ログファイル - `src/utils/logger.py`
- **Webダッシュボード**: HTML/CSS/JS - `src/monitoring/dashboard/`
- **クラウド保存**: クラウドAPI - `src/storage/cloud/`

---

本ガイドに記載されていない問題が発生した場合は、`--debug`オプションを使用してデバッグ情報を確認し、ログファイルを参照してください。