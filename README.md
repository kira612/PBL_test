# Research Lab Camera-Based Monitoring System

研究室向けカメラベース監視システム - 位置推定・行動検出・入退出管理

## 概要

このプロジェクトは、研究室などの閉鎖空間における人物の位置推定と行動検出を行うカメラベースの監視システムです。

### 主な機能

- **Phase 1**: 位置推定と行動検出
  - 人物検出・追跡
  - 研究室内での位置推定
  - 行動検出（立つ・座る・パソコンに触る等）
  
- **Phase 2**: 入退出管理システム

### 技術仕様

- **環境**: 3m × 4m の研究室
- **カメラ**: 複数台対応可能
- **処理**: リアルタイム処理
- **ハードウェア**: GPU使用可能
- **使用ライブラリ**: OpenCV, YOLO, MediaPipe等（柔軟に選択）

### 研究目的

各手法の精度評価と比較研究を行い、実装後の性能を研究対象として扱います。

## 環境設定

### 必要なソフトウェア

- Docker
- Docker Compose
- Git

### セットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd PBL_test

# イメージのビルド
docker-compose build

# コンテナの起動
docker-compose up -d

# コンテナに入る
docker-compose exec app bash
```

## 使用方法

```bash
# アプリケーションの実行
docker-compose exec app python main.py

# または
docker-compose run app python main.py
```

## プロジェクト構成

```
PBL_test/
├── .gitignore
├── .github/
│   └── workflows/
├── README.md
├── CLAUDE.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── main.py
└── src/
    └── （モジュールファイル）
```

## テスト

```bash
# テストの実行
docker-compose exec app python -m pytest
```