# システム構成図 - 研究室向けカメラベース監視システム
# System Architecture - Laboratory Camera-based Monitoring System

## システム概要

本システムは、研究室環境における人物の検出、位置推定、行動認識を統合的に行うモジュラー設計のカメラベース監視システムです。

## 全体アーキテクチャ

```mermaid
graph TB
    subgraph "Input Layer"
        Camera[カメラ入力<br/>Camera Input]
        Config[設定ファイル<br/>Configuration Files]
    end

    subgraph "Core Processing Layer"
        CameraManager[カメラ管理<br/>src/camera/manager.py]
        PersonDetector[人物検出<br/>src/detection/detector.py]
        PositionEstimator[位置推定<br/>src/position_estimation/estimator.py]
        ActionRecognizer[行動認識<br/>src/action_recognition/recognizer.py]
    end

    subgraph "Visualization Layer"
        MonitoringDisplay[監視表示<br/>src/monitoring/display/display.py]
    end

    subgraph "Coordination Layer"
        Coordinator[システム統合<br/>src/monitoring/coordinator.py]
    end

    subgraph "Output Layer"
        Display[リアルタイム表示<br/>Real-time Display]
        Storage[データ保存<br/>Data Storage]
        Statistics[統計情報<br/>Statistics]
    end

    Camera --> CameraManager
    Config --> Coordinator
    CameraManager --> PersonDetector
    PersonDetector --> PositionEstimator
    PersonDetector --> ActionRecognizer
    CameraManager --> Coordinator
    PersonDetector --> Coordinator
    PositionEstimator --> Coordinator
    ActionRecognizer --> Coordinator
    Coordinator --> MonitoringDisplay
    Coordinator --> Display
    Coordinator --> Storage
    Coordinator --> Statistics
    MonitoringDisplay --> Display
```

## モジュール詳細構成

### 1. カメラ管理層 (Camera Management Layer)

```mermaid
graph LR
    subgraph "Camera Management"
        CM[CameraManager]
        MCM[MultiCameraManager]
        
        CM --> |manages| Device[Camera Device]
        MCM --> |manages multiple| CM
        
        CM --> |provides| FrameGen[Frame Generator]
        CM --> |provides| AsyncGen[Async Generator]
        CM --> |provides| Stats[Camera Statistics]
    end
```

**主要機能:**
- カメラデバイスの初期化と管理 (`src/camera/manager.py`)
- フレーム取得とバッファリング
- 複数カメラの同期管理 (`src/camera/multi_camera/`)
- 統計情報の収集
- カメラドライバ管理 (`src/camera/drivers/`)

### 2. 人物検出層 (Person Detection Layer)

```mermaid
graph TB
    subgraph "Detection Methods"
        YOLO[YOLO Detector<br/>src/detection/yolo/<br/>・高速検出<br/>・バウンディングボックス]
        MediaPipe[MediaPipe Detector<br/>src/detection/mediapipe/<br/>・姿勢推定<br/>・ランドマーク検出]
    end
    
    subgraph "Unified Interface"
        PersonDetector[Person Detector<br/>統合インターフェース]
    end
    
    subgraph "Output"
        Detection[Detection Results<br/>・バウンディングボックス<br/>・信頼度<br/>・中心座標]
        Pose[Pose Information<br/>・関節位置<br/>・可視性スコア<br/>・姿勢推定]
    end
    
    YOLO --> PersonDetector
    MediaPipe --> PersonDetector
    PersonDetector --> Detection
    PersonDetector --> Pose
```

**検出方法比較:**

| 方法 | 精度 | 速度 | GPU要件 | 出力情報 |
|------|------|------|---------|----------|
| YOLO | 高 | 高 | 推奨 | バウンディングボックス |
| MediaPipe | 中 | 中 | 不要 | 姿勢ランドマーク |

### 3. 位置推定層 (Position Estimation Layer)

```mermaid
graph TB
    subgraph "Position Methods"
        BBox[BBox Center<br/>src/position_estimation/estimator.py<br/>・最も軽量<br/>・基本的な精度]
        Perspective[Perspective Mapping<br/>src/position_estimation/perspective/<br/>・高精度<br/>・要較正]
        Depth[Depth Estimation<br/>src/position_estimation/ai_models/<br/>・中程度精度<br/>・人物サイズベース]
    end
    
    subgraph "Room Coordinate System"
        Room[Room Dimensions<br/>4m × 3m × 2.5m]
        Coordinates[座標系<br/>X: 左壁からの距離<br/>Y: 前壁からの距離]
    end
    
    subgraph "Output"
        Position[Room Position<br/>・X, Y座標 (メートル)<br/>・信頼度<br/>・タイムスタンプ]
        OccupancyMap[占有マップ<br/>・10cm解像度<br/>・密度情報]
    end
    
    BBox --> Position
    Perspective --> Position
    Depth --> Position
    Room --> Coordinates
    Position --> OccupancyMap
```

**位置推定方法比較:**

| 方法 | 精度 | 較正要件 | 計算負荷 | 適用場面 |
|------|------|----------|----------|----------|
| BBox Center | 低 | 不要 | 軽量 | 基本的な位置把握 |
| Perspective Mapping | 高 | 必要 | 中 | 正確な位置測定 |
| Depth Estimation | 中 | 不要 | 中 | バランス重視 |

### 4. 行動認識層 (Action Recognition Layer)

```mermaid
graph TB
    subgraph "Recognition Methods"
        PoseAction[Pose-based Recognition<br/>src/action_recognition/pose/<br/>・関節角度解析<br/>・ランドマーク距離]
        BBoxAction[BBox-based Recognition<br/>src/action_recognition/bbox/<br/>・アスペクト比解析<br/>・移動パターン]
    end
    
    subgraph "Action Types"
        Standing[Standing<br/>立っている]
        Sitting[Sitting<br/>座っている]
        Walking[Walking<br/>歩いている]
        Computer[Computer Interaction<br/>コンピュータ操作]
        Unknown[Unknown<br/>不明]
    end
    
    subgraph "Analysis Features"
        JointAngles[関節角度<br/>・肘角度<br/>・膝角度]
        BodyRatios[体型比率<br/>・縦横比<br/>・重心位置]
        Movement[移動パターン<br/>・位置履歴<br/>・速度解析]
    end
    
    PoseAction --> JointAngles
    BBoxAction --> BodyRatios
    BBoxAction --> Movement
    
    JointAngles --> Standing
    JointAngles --> Sitting
    JointAngles --> Computer
    BodyRatios --> Standing
    BodyRatios --> Sitting
    Movement --> Walking
```

**行動認識アルゴリズム:**

1. **Standing (立位)**
   - 肩と腰の垂直距離 > 閾値
   - 足首が腰より下
   - アスペクト比 > 2.0

2. **Sitting (座位)**
   - 肩と腰の距離 < 閾値
   - 膝が腰より上
   - アスペクト比 < 1.5

3. **Computer Interaction (PC操作)**
   - 両手首の距離 < 閾値
   - 肘角度 60-120度
   - 座位姿勢との組み合わせ

4. **Walking (歩行)**
   - 位置履歴での移動検出
   - 足の非対称配置
   - 継続的な位置変化

### 5. 可視化層 (Visualization Layer)

```mermaid
graph TB
    subgraph "Display Components"
        DisplayManager[Display Manager<br/>src/monitoring/display/display.py<br/>・ウィンドウ管理<br/>・レンダリング制御]
        BBoxRenderer[BBox Renderer<br/>src/monitoring/display/<br/>・バウンディングボックス描画<br/>・ラベル表示]
        InfoOverlay[Info Overlay<br/>src/monitoring/display/<br/>・FPS表示<br/>・統計情報]
        RoomLayout[Room Layout<br/>src/monitoring/display/<br/>・部屋俯瞰図<br/>・位置マーカー]
    end
    
    subgraph "Display Modes"
        WindowMode[Window Mode<br/>OpenCVウィンドウ表示]
        HeadlessMode[Headless Mode<br/>バックグラウンド処理]
        NoneMode[None Mode<br/>表示なし]
    end
    
    subgraph "Visual Elements"
        PersonBox[Person BBox<br/>・緑色の枠<br/>・信頼度表示]
        PositionInfo[Position Info<br/>・座標表示<br/>・距離表示]
        ActionLabel[Action Label<br/>・行動タイプ<br/>・色分け表示]
        SystemStats[System Stats<br/>・FPS<br/>・検出数]
    end
    
    DisplayManager --> BBoxRenderer
    DisplayManager --> InfoOverlay
    DisplayManager --> RoomLayout
    
    BBoxRenderer --> PersonBox
    InfoOverlay --> PositionInfo
    InfoOverlay --> ActionLabel
    InfoOverlay --> SystemStats
    
    DisplayManager --> WindowMode
    DisplayManager --> HeadlessMode
    DisplayManager --> NoneMode
```

#### 可視化機能の特徴
- **リアルタイム表示**: カメラ映像にリアルタイムで検出結果をオーバーレイ
- **多様な表示モード**: ウィンドウ表示、ヘッドレス、表示なしから選択可能
- **豊富な情報表示**: 検出、位置、行動、システム統計を統合表示
- **インタラクティブ操作**: ESCキーやウィンドウ閉じでシステム終了
- **カスタマイズ可能**: 表示項目や色設定を設定ファイルで制御

---

### 6. システム統合層 (System Coordination Layer)

```mermaid
graph TB
    subgraph "Monitoring Coordinator"
        Init[システム初期化<br/>src/monitoring/coordinator.py<br/>Component Initialization]
        MainLoop[メインループ<br/>src/monitoring/coordinator.py<br/>Main Processing Loop]
        Visualize[可視化処理<br/>src/monitoring/display/<br/>Visualization]
        Stats[統計処理<br/>src/storage/<br/>Statistics]
    end
    
    subgraph "Data Flow"
        Frame[フレーム取得] --> Detection[人物検出]
        Detection --> Position[位置推定]
        Detection --> Action[行動認識]
        Position --> Integration[結果統合]
        Action --> Integration
        Integration --> Visualize
    end
    
    subgraph "Output Management"
        Display[リアルタイム表示]
        Save[結果保存]
        Log[ログ出力]
    end
    
    Init --> MainLoop
    MainLoop --> Frame
    Visualize --> Display
    Stats --> Save
    Stats --> Log
```

## データフロー (Data Flow)

### リアルタイム処理フロー

```mermaid
sequenceDiagram
    participant Camera as カメラ
    participant Detector as 人物検出
    participant Position as 位置推定
    participant Action as 行動認識
    participant Coord as コーディネータ
    participant Visual as 可視化
    participant Display as 表示

    loop フレーム処理
        Camera->>Detector: フレーム送信
        Detector->>Detector: 人物検出処理
        Detector->>Position: 検出結果送信
        Detector->>Action: 検出結果送信
        Position->>Position: 位置推定処理
        Action->>Action: 行動認識処理
        Position->>Coord: 位置情報送信
        Action->>Coord: 行動情報送信
        Coord->>Coord: 結果統合処理
        Coord->>Visual: 統合結果送信
        Visual->>Visual: オーバーレイ描画
        Visual->>Display: 可視化フレーム送信
    end
```

### 設定管理フロー

```mermaid
graph LR
    subgraph "Configuration Sources"
        Default[デフォルト設定<br/>src/config/config.py]
        File[設定ファイル<br/>YAML/JSON]
        CLI[コマンドライン引数]
    end
    
    subgraph "Configuration Processing"
        Parser[設定パーサー]
        Validator[設定検証]
        Merger[設定統合]
    end
    
    subgraph "System Components"
        Camera[カメラ設定<br/>src/camera/]
        Detection[検出設定<br/>src/detection/]
        Position[位置推定設定<br/>src/position_estimation/]
        Action[行動認識設定<br/>src/action_recognition/]
        System[システム設定<br/>src/monitoring/]
    end
    
    Default --> Parser
    File --> Parser
    CLI --> Parser
    Parser --> Validator
    Validator --> Merger
    Merger --> Camera
    Merger --> Detection
    Merger --> Position
    Merger --> Action
    Merger --> System
```

## パフォーマンス特性

### 処理時間分析

| コンポーネント | 処理時間 (ms) | CPU使用率 | GPU使用率 |
|----------------|---------------|-----------|-----------|
| カメラ取得 | 1-5 | 低 | - |
| YOLO検出 | 10-50 | 中 | 高 |
| MediaPipe検出 | 15-30 | 中 | 低 |
| 位置推定 | 1-5 | 低 | - |
| 行動認識 | 5-15 | 低 | - |
| 可視化 | 5-10 | 低 | - |

### スケーラビリティ

```mermaid
graph TB
    subgraph "Single Camera"
        SC[1台カメラ<br/>30 FPS<br/>1人対応]
    end
    
    subgraph "Multi Camera"
        MC[複数カメラ<br/>15-20 FPS/台<br/>複数人対応]
    end
    
    subgraph "Distributed"
        DC[分散処理<br/>エッジ+クラウド<br/>大規模対応]
    end
    
    SC --> MC
    MC --> DC
```

## 拡張性設計

### モジュール拡張ポイント

1. **新しい検出アルゴリズム**
   - `DetectionMethod` Enumに追加 (`src/detection/detector.py`)
   - 新しい検出クラスを実装 (`src/detection/新しい手法/`)
   - `PersonDetector`に統合

2. **新しい位置推定方法**
   - `PositionMethod` Enumに追加 (`src/position_estimation/estimator.py`)
   - 新しい推定クラスを実装 (`src/position_estimation/新しい手法/`)
   - `PositionEstimator`に統合

3. **新しい行動タイプ**
   - `ActionType` Enumに追加 (`src/action_recognition/recognizer.py`)
   - 認識ロジックを追加 (`src/action_recognition/pose/` または `src/action_recognition/bbox/`)
   - 可視化対応を追加 (`src/monitoring/display/`)

4. **データ保存形式**
   - 新しい出力フォーマット (`src/storage/processor.py`)
   - データベース連携 (`src/storage/local/` または `src/storage/cloud/`)
   - クラウド保存 (`src/storage/cloud/`)

### 研究応用展開

```mermaid
graph TB
    subgraph "Current System"
        Basic[基本監視システム<br/>src/monitoring/coordinator.py<br/>・人物検出<br/>・位置推定<br/>・行動認識]
    end
    
    subgraph "Phase 2 Extensions"
        Entry[入退出管理<br/>src/monitoring/tracking/<br/>・顔認識<br/>・ID管理]
        Analysis[行動分析<br/>src/action_recognition/<br/>・時系列解析<br/>・パターン検出]
        Multi[マルチカメラ<br/>src/camera/multi_camera/<br/>・3D追跡<br/>・死角対応]
    end
    
    subgraph "Research Applications"
        Workspace[ワークスペース分析<br/>src/monitoring/dashboard/<br/>・作業効率測定<br/>・空間利用評価]
        Safety[安全管理<br/>src/monitoring/tracker.py<br/>・異常行動検出<br/>・緊急時対応]
        Privacy[プライバシー保護<br/>src/utils/<br/>・匿名化処理<br/>・GDPR対応]
    end
    
    Basic --> Entry
    Basic --> Analysis
    Basic --> Multi
    Entry --> Workspace
    Analysis --> Safety
    Multi --> Privacy
```

この設計により、研究目的での柔軟な拡張と各手法の精度評価・比較研究が可能となります。