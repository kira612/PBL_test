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
- **Docker**: 20.10+ および Docker Compose
- **Python**: 3.11+ (Docker使用時は不要)

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

### 2.2 Docker環境での実行（推奨）
```bash
# コンテナの構築と起動
docker-compose up -d

# コンテナ内でシステム実行
docker-compose exec app python main.py
```

### 2.3 ローカル環境での実行
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
from src.core.camera import CameraManager

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

### 5.2 人物検出の単独使用
```python
from src.core.detector import PersonDetector, DetectionMethod

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

### 5.3 位置推定の単独使用
```python
from src.vision.position_estimator import PositionEstimator, PositionMethod, RoomDimensions

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

### 5.4 行動認識の単独使用
```python
from src.vision.action_recognizer import ActionRecognizer

# 行動認識器初期化
recognizer = ActionRecognizer(use_pose=True)

# 行動認識実行
actions = recognizer.recognize_actions(detections, poses, (480, 640))
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

### 6.3 Docker関連の問題

#### コンテナが起動しない
```bash
# コンテナログ確認
docker-compose logs app

# コンテナ再構築
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### カメラアクセスエラー (Docker)
```yaml
# docker-compose.ymlでデバイスマッピング確認
devices:
  - /dev/video0:/dev/video0
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

---

## 付録

### A. サポートされている検出方法
1. **YOLO (You Only Look Once)**
   - 高速・高精度
   - GPU推奨
   - モデルサイズ: yolov8n.pt (6MB) ～ yolov8x.pt (136MB)

2. **MediaPipe**
   - CPU最適化
   - 姿勢情報付き
   - リアルタイム処理

### B. サポートされている位置推定方法
1. **bbox_center**: 最も軽量、基本的な精度
2. **perspective_mapping**: 高精度、要較正
3. **depth_estimation**: 中程度精度、設定不要

### C. 認識可能な行動
- Standing (立っている)
- Sitting (座っている)
- Walking (歩いている)
- Computer Interaction (コンピュータ操作)
- Unknown (不明)

### D. 出力形式
- **リアルタイム表示**: OpenCVウィンドウ
- **画像保存**: JPEG形式
- **データ出力**: JSON形式（実装予定）
- **統計情報**: ログファイル

---

本ガイドに記載されていない問題が発生した場合は、`--debug`オプションを使用してデバッグ情報を確認し、ログファイルを参照してください。