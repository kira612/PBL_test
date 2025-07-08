# Development Guidelines

This document contains critical information about working with this codebase. Follow these guidelines precisely.
（このドキュメントには、このコードベースで作業するための重要な情報が含まれています。これらのガイドラインに正確に従ってください。）

## Project Requirements（プロジェクトの要件定義）

### Project Purpose and Goals（プロジェクトの目的と目標）
- **Primary Goal**: 研究室などの閉鎖空間におけるカメラベースの監視システム開発
- **Phase 1**: 位置推定と行動検出の実装
- **Phase 2**: 入退出管理機能の追加
- **Research Focus**: 各手法の精度評価と比較研究

### Target Users（対象ユーザー）
- 研究室に入るすべての人（学生、研究員、教員）
- 研究目的での利用を想定

### Environment Specifications（環境仕様）
- **Space**: 3m × 4m の研究室
- **Camera**: 複数台対応可能
- **Processing**: リアルタイム処理を目指す
- **Hardware**: GPU使用可能
- **Operation**: 24時間稼働が望ましい（停止も許容）

### Main Features and Functionality（主な機能と機能性）

#### Core Features（コア機能）
1. **Person Detection**: 人物検出・追跡
2. **Position Estimation**: 研究室内での位置推定
3. **Action Recognition**: 行動検出
   - 立つ・座る
   - パソコンに触る
   - その他の基本的な行動

#### Future Features（将来機能）
- 入退出管理システム
- 顔認識（優先度低）
- 深層学習による深度推定（必要に応じて）

#### Visualization（可視化）
- リアルタイム監視画面
- データダッシュボード
- 統計情報の表示

### Technical Specifications（技術仕様）
- **Language**: Python
- **Computer Vision Libraries**（柔軟な選択）:
  - OpenCV
  - YOLO
  - MediaPipe
  - その他必要に応じて追加
- **Framework**: Docker環境での開発
- **Data Storage**: 保存期間制限なし
- **Security**: 最小限（研究目的のため）

### Performance Requirements（パフォーマンス要件）
- **Note**: 厳密な定義はせず、実装後の精度評価も研究対象
- **Target**: リアルタイム処理
- **Hardware**: GPU活用によるパフォーマンス向上

### Security Considerations（セキュリティの考慮事項）
- **Priority**: 低（研究目的のため）
- **Access Control**: 特に制限なし
- **Data Protection**: 基本的な保護のみ実装

## Core Development Rules（コア開発ルール）

1. Package Management（パッケージ管理）
   - Use pip for package management（パッケージ管理にはpipを使用）
   - Installation: `pip install package`（インストール）
   - Development dependencies: `pip install -r requirements-dev.txt`（開発依存関係）
   - Production dependencies: `pip install -r requirements.txt`（本番依存関係）

2. Code Quality（コード品質）
   - Type hints required for all code（すべてのコードに型ヒントが必要）
   - Public APIs must have docstrings（パブリックAPIにはdocstringが必要）
   - Functions must be focused and small（関数は集約され小さくする）
   - Follow existing patterns exactly（既存のパターンを正確に従う）
   - Line length: 88 chars maximum（行の長さは最大88文字）

3. Testing Requirements（テスト要件）
   - Framework: `python -m pytest`（フレームワーク）
   - Async testing: use anyio, not asyncio（非同期テストはanyioを使用、asyncioは使わない）
   - Coverage: test edge cases and errors（カバレッジ：エッジケースとエラーをテスト）
   - New features require tests（新機能にはテストが必要）
   - Bug fixes require regression tests（バグ修正には回帰テストが必要）

## Docker Environment（Docker環境）

- Development is done inside Docker containers（開発はDockerコンテナ内で行う）
- Main commands:（主なコマンド）
  ```bash
  # Start development environment（開発環境の開始）
  docker-compose up -d
  
  # Run application（アプリケーションの実行）
  docker-compose exec app python main.py
  
  # Run tests（テストの実行）
  docker-compose exec app python -m pytest
  
  # Access container shell（コンテナシェルへのアクセス）
  docker-compose exec app bash
  ```

## Code Formatting（コードフォーマット）

1. Ruff
   - Format: `python -m ruff format .`（フォーマット）
   - Check: `python -m ruff check .`（チェック）
   - Fix: `python -m ruff check . --fix`（修正）
   - Critical issues:（重要な問題）
     - Line length (88 chars)（行の長さ88文字）
     - Import sorting (I001)（インポートソート）
     - Unused imports（未使用のインポート）

2. Type Checking（型チェック）
   - Tool: `python -m pyright`（ツール）
   - Requirements:（要件）
     - Explicit None checks for Optional（OptionalにはNoneチェックを明示）
     - Type narrowing for strings（文字列の型絞り込み）

## Error Resolution（エラー解決）

1. CI Failures（CI障害）
   - Fix order:（修正順序）
     1. Formatting（書式設定）
     2. Type errors（型エラー）
     3. Linting（リンティング）
   - Type errors:（型エラー）
     - Get full line context（完全な行のコンテキストを取得）
     - Check Optional types（オプションタイプを確認）
     - Add type narrowing（型の絞り込みを追加）
     - Verify function signatures（関数シグネチャを検証）

2. Common Issues（よくある問題）
   - Line length:（行の長さ）
     - Break strings with parentheses（括弧で文字列を区切る）
     - Multi-line function calls（複数行の関数呼び出し）
     - Split imports（分割インポート）
   - Types:（型）
     - Add None checks（Noneチェックを追加）
     - Narrow string types（文字列型を絞り込む）
     - Match existing patterns（既存のパターンに一致）
   - Pytest:
     - If the tests aren't finding the anyio pytest mark, try adding PYTEST_DISABLE_PLUGIN_AUTOLOAD=""
       to the start of the pytest run command eg:
       （テストでanyio pytestマークが見つからない場合は、pytest実行コマンドの先頭にPYTEST_DISABLE_PLUGIN_AUTOLOAD=""を追加）
       `PYTEST_DISABLE_PLUGIN_AUTOLOAD="" python -m pytest`

3. Best Practices（ベストプラクティス）
   - Check git status before commits（コミット前にgitステータスを確認）
   - Run formatters before type checks（型チェックの前にフォーマッタを実行）
   - Keep changes minimal（変更は最小限に抑える）
   - Follow existing patterns（既存のパターンに従う）
   - Document public APIs（パブリックAPIをドキュメント化）
   - Test thoroughly（徹底的にテスト）

## Project Structure（プロジェクト構造）

```
PBL_test/
├── .gitignore           # Git ignore file（Git無視ファイル）
├── .github/workflows/   # GitHub Actions
├── README.md           # Project documentation（プロジェクトドキュメント）
├── CLAUDE.md           # This file（このファイル）
├── Dockerfile          # Docker configuration（Docker設定）
├── docker-compose.yml  # Docker Compose setup（Docker Compose設定）
├── requirements.txt    # Python dependencies（Python依存関係）
├── main.py            # Main application（メインアプリケーション）
└── src/               # Source code（ソースコード）
    └── (module files) # （モジュールファイル）
```

## Git Workflow（Gitワークフロー）

- For commits fixing bugs or adding features based on user reports add:
  （ユーザーレポートに基づくバグ修正や機能追加のコミット時に追加）
  ```bash
  git commit --trailer "Reported-by:<name>"
  ```
  Where `<name>` is the name of the user.（`<name>`はユーザー名）

- For commits related to a Github issue, add:
  （GitHub issueに関連するコミット時に追加）
  ```bash
  git commit --trailer "Github-Issue:#<number>"
  ```