# 研究室向けカメラベース監視システム
# Laboratory Camera-based Monitoring System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

研究室環境における人物の検出、位置推定、行動認識を統合的に行うリアルタイム監視システムです。

A real-time monitoring system that integrates person detection, position estimation, and action recognition for laboratory environments.

## 🎯 プロジェクト概要 (Project Overview)

このシステムは、3m × 4m の研究室環境において以下の機能を提供します：

- **人物検出** (Person Detection): YOLO/MediaPipeによる高精度検出
- **位置推定** (Position Estimation): 部屋座標系での正確な位置特定
- **行動認識** (Action Recognition): 立つ・座る・歩く・PC操作の識別
- **リアルタイム可視化** (Real-time Visualization): バウンディングボックス・位置・行動情報の統合表示
- **マルチモード表示** (Multi-mode Display): ウィンドウ・ヘッドレス・表示なしから選択可能

## 🚀 主な特徴 (Key Features)

### ✨ 多重検出手法
- **YOLO**: 高速・高精度な物体検出
- **MediaPipe**: CPU最適化された姿勢推定

### 📍 柔軟な位置推定
- **バウンディングボックス中心**: 軽量で基本的な位置把握
- **透視変換**: 高精度な実世界座標変換
- **深度推定**: 人物サイズベースの距離測定

### 🎭 包括的行動認識
- **Standing** (立位): 直立姿勢の検出
- **Sitting** (座位): 着座姿勢の識別
- **Walking** (歩行): 移動パターンの認識
- **Computer Interaction** (PC操作): タイピング姿勢の判定

### 🖥️ 高度な可視化機能
- **リアルタイム表示**: カメラ映像への検出結果オーバーレイ
- **バウンディングボックス**: 人物検出の可視化（信頼度表示付き）
- **位置情報**: 部屋座標と距離の数値表示
- **行動ラベル**: 認識された行動の色分け表示
- **システム統計**: FPS、検出数、タイムスタンプ表示
- **部屋レイアウト**: 俯瞰図での位置マーカー表示
- **マルチモード**: ウィンドウ・ヘッドレス・表示なしから選択

### 🔧 研究指向設計
- モジュラー構成による柔軟な拡張性
- 各手法の精度評価・比較研究対応
- 設定ファイルによる詳細なカスタマイズ

## 📋 システム要件 (System Requirements)

### ハードウェア
- **CPU**: Intel i5以上 (GPU使用推奨)
- **RAM**: 8GB以上
- **カメラ**: USB Webカメラ (1080p推奨)
- **ストレージ**: 5GB以上

### ソフトウェア
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **Docker**: 20.10+ および Docker Compose
- **Python**: 3.11+ (Docker使用時は不要)

## 🛠️ インストール (Installation)

### Docker使用（推奨）
```bash
# リポジトリのクローン
git clone https://github.com/yourusername/laboratory-monitoring-system.git
cd laboratory-monitoring-system

# Docker環境の構築
docker-compose up -d

# システム実行
docker-compose exec app python main.py
```

### ローカル環境
```bash
# 依存関係のインストール
pip install -r requirements.txt

# システム実行
python main.py
```

## 🎮 使用方法 (Usage)

### 基本実行
```bash
# デフォルト設定で実行（表示なし）
python main.py

# ウィンドウ表示で実行
python main.py --display window

# 詳細情報付きウィンドウ表示
python main.py --display window --show-fps --show-info

# カメラIDを指定してウィンドウ表示
python main.py --camera-id 1 --display window

# 設定ファイルを使用
python main.py --config config.yaml --display window

# デバッグモード
python main.py --debug --display window
```

### 実行中の操作
- **Ctrl+C**: システム終了（コマンドライン）
- **ESCキー**: システム終了（ウィンドウ表示時）
- **ウィンドウ×ボタン**: 安全な終了（ウィンドウ表示時）

### 可視化オプション
- **--display**: 表示モード選択
  - `none`: 表示なし（デフォルト）
  - `window`: OpenCVウィンドウ表示
  - `headless`: バックグラウンド処理
- **--show-fps**: FPSカウンター表示
- **--show-info**: 検出・位置・行動情報表示

## ⚙️ 設定 (Configuration)

### 基本設定例
```yaml
# カメラ設定
camera:
  camera_id: 0
  width: 640
  height: 480
  fps: 30

# 検出設定
detection:
  method: "yolo"  # または "mediapipe"
  confidence_threshold: 0.6

# 位置推定設定
position:
  method: "bbox_center"  # または "perspective_mapping", "depth_estimation"

# 行動認識設定
action:
  use_pose: true
  confidence_threshold: 0.3
```

詳細な設定オプションは [`config.yaml`](config.yaml) を参照してください。

## 📊 パフォーマンス (Performance)

| 検出方法 | FPS | CPU使用率 | GPU使用率 | 精度 |
|----------|-----|-----------|-----------|------|
| YOLO | 25-30 | 中 | 高 | 高 |
| MediaPipe | 20-25 | 中 | 低 | 中 |

※ 性能は Intel i7 + GTX 1660 環境での測定値

## 📁 プロジェクト構造 (Project Structure)

```
PBL_test/
├── 📁 src/                     # ソースコード
│   ├── 📁 action_recognition/  # 行動認識システム
│   │   ├── 📁 bbox/           # BBox基盤行動認識
│   │   ├── 📁 pose/           # 姿勢基盤行動認識
│   │   ├── recognizer.py      # 行動認識メインモジュール
│   │   └── mediapipe_handler.py # MediaPipeユーティリティ
│   ├── 📁 camera/             # カメラ管理システム
│   │   ├── 📁 drivers/        # カメラドライバー
│   │   ├── 📁 multi_camera/   # マルチカメラサポート
│   │   └── manager.py         # カメラマネージャー
│   ├── 📁 config/             # 設定管理
│   │   └── config.py          # 設定ローダー
│   ├── 📁 detection/          # 人物検出システム
│   │   ├── 📁 yolo/           # YOLO基盤検出
│   │   ├── 📁 mediapipe/      # MediaPipe基盤検出
│   │   └── detector.py        # 人物検出メインモジュール
│   ├── 📁 models/             # データモデル
│   │   └── models.py          # コアデータ構造
│   ├── 📁 monitoring/         # 監視システム統合
│   │   ├── 📁 dashboard/      # ダッシュボード機能
│   │   │   ├── dashboard.py   # メインダッシュボード
│   │   │   └── statistics.py  # 統計表示
│   │   ├── 📁 display/        # 表示コンポーネント
│   │   │   ├── display.py     # メイン表示モジュール
│   │   │   └── stream_viewer.py # ストリームビューアー
│   │   ├── coordinator.py     # システムコーディネーター
│   │   └── tracker.py         # オブジェクトトラッカー
│   ├── 📁 position_estimation/ # 位置推定システム
│   │   ├── 📁 ai_models/      # AI基盤位置推定
│   │   │   ├── mediapipe.py   # MediaPipe位置推定
│   │   │   ├── midas.py       # MiDaS深度推定
│   │   │   └── dpt.py         # DPT深度推定
│   │   ├── 📁 perspective/    # 透視変換基盤推定
│   │   │   └── perspective.py # 透視変換
│   │   ├── estimator.py       # 位置推定メインモジュール
│   │   ├── interface.py       # 位置推定インターフェース
│   │   └── manager.py         # 位置推定マネージャー
│   ├── 📁 storage/            # データストレージ
│   │   ├── 📁 local/          # ローカルストレージ
│   │   ├── 📁 cloud/          # クラウドストレージ
│   │   ├── processor.py       # データプロセッサー
│   │   └── storage.py         # ストレージマネージャー
│   ├── 📁 tests/              # テストスイート
│   │   ├── test_detector.py   # 検出テスト
│   │   ├── test_position_estimator.py # 位置推定テスト
│   │   └── test_tracker.py    # トラッカーテスト
│   ├── 📁 ui/                 # ユーザーインターフェース
│   │   ├── 📁 web/            # Webインターフェース
│   │   └── 📁 desktop/        # デスクトップインターフェース
│   └── 📁 utils/              # ユーティリティ関数
│       ├── helpers.py         # ヘルパー関数
│       └── logger.py          # ログユーティリティ
├── 📁 docs/                   # ドキュメント
│   ├── API_Documentation.md   # API仕様書
│   ├── Usage_Guide.md         # 使用ガイド
│   └── System_Architecture.md # システム構成図
├── 📁 .devcontainer/          # VS Code開発コンテナ
├── 🐳 docker-compose.yml      # Docker構成
├── 📄 requirements.txt        # Python依存関係
├── ⚙️ config.yaml            # 設定ファイル
└── 🚀 main.py                # メインエントリーポイント
```

## 📚 ドキュメント (Documentation)

- 📖 [API仕様書](docs/API_Documentation.md) - 全関数・クラスの詳細仕様
- 📘 [使用ガイド](docs/Usage_Guide.md) - インストールから運用まで
- 🏗️ [システム構成図](docs/System_Architecture.md) - アーキテクチャと設計思想

## 🔬 研究応用 (Research Applications)

### 精度評価研究
- 複数検出手法の性能比較
- 位置推定精度の定量評価
- 行動認識精度の統計分析

### 拡張研究
- 新しい行動パターンの追加
- マルチカメラ統合
- 深層学習モデルの組み込み

### データ分析
- 研究室利用パターンの分析
- 作業効率の定量化
- 空間利用最適化の研究

## 🛡️ プライバシーとセキュリティ

- **ローカル処理**: データは外部送信されません
- **研究目的設計**: 最小限のセキュリティ実装
- **カスタマイズ可能**: 必要に応じてセキュリティ強化可能

## 🤝 コントリビューション (Contributing)

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📝 ライセンス (License)

このプロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 🙏 謝辞 (Acknowledgments)

- [YOLO](https://github.com/ultralytics/ultralytics) - 高性能物体検出
- [MediaPipe](https://github.com/google/mediapipe) - リアルタイム姿勢推定
- [OpenCV](https://opencv.org/) - コンピュータビジョン基盤

## 📞 サポート (Support)

問題が発生した場合は、以下の手順で対処してください：

1. [使用ガイド](docs/Usage_Guide.md)のトラブルシューティングを確認
2. [Issues](https://github.com/yourusername/laboratory-monitoring-system/issues)で既存の問題を検索
3. 新しいIssueを作成して詳細を報告

## 🎯 今後の予定 (Roadmap)

- [ ] 入退出管理システムの実装
- [ ] 顔認識機能の追加
- [ ] Webダッシュボードの開発
- [ ] マルチカメラ対応
- [ ] データ分析ツールの統合
- [ ] クラウド連携機能

---

<div align="center">

**⭐ このプロジェクトが役に立った場合は、スターをつけてください！**

Made with ❤️ for laboratory research

</div>