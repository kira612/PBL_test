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
   - Use conda environment for package management（パッケージ管理にはconda環境を使用）
   - Environment activation: `conda activate pbl_test`（環境のアクティベート）
   - Package installation: `pip install package` (within conda environment)（パッケージインストール（conda環境内で））
   - Development dependencies: `pip install -r requirements-conda.txt`（開発依存関係）
   - Production dependencies: `pip install -r requirements-conda.txt`（本番依存関係）

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

## Anaconda Environment（Anaconda環境）

- Development is done inside Anaconda conda environment（開発はAnacondaのconda環境内で行う）
- Main commands:（主なコマンド）
  ```bash
  # Activate development environment（開発環境のアクティベート）
  conda activate pbl_test
  
  # Run application（アプリケーションの実行）
  python main.py
  
  # Run tests（テストの実行）
  python -m pytest
  
  # Install packages（パッケージのインストール）
  pip install -r requirements-conda.txt
  
  # Deactivate environment（環境の非アクティベート）
  conda deactivate
  ```

## Code Formatting（コードフォーマット）

1. Ruff
   - Format: `ruff format .`（フォーマット）
   - Check: `ruff check .`（チェック）
   - Fix: `ruff check . --fix`（修正）
   - Critical issues:（重要な問題）
     - Line length (88 chars)（行の長さ88文字）
     - Import sorting (I001)（インポートソート）
     - Unused imports（未使用のインポート）

2. Type Checking（型チェック）
   - Tool: `pyright`（ツール）
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

### Branch Strategy（ブランチ戦略）

This project uses a feature-branch workflow with the following structure:
このプロジェクトは以下の構造を持つフィーチャーブランチワークフローを使用します：

```
main (本番・安定版)
├── future (開発統合ブランチ)
│   ├── feature/person-detection-enhancement
│   ├── feature/position-estimation-improvement
│   ├── feature/action-recognition-expansion
│   ├── feature/web-dashboard
│   ├── feature/multi-camera-support
│   ├── feature/face-recognition
│   └── feature/entry-exit-management
├── hotfix/critical-bug-fix
└── release/v1.0.0
```

#### Branch Types（ブランチタイプ）

1. **main**: 本番環境用の安定版（Production-ready stable version）
   - 完全にテスト済みのコード（Fully tested code）
   - ドキュメント完全同期（Documentation fully synchronized）
   - リリース可能な状態（Ready for release）

2. **future**: 開発統合ブランチ（Development integration branch）
   - 新機能の統合テスト（Integration testing for new features）
   - フィーチャーブランチのマージ先（Target for feature branch merges）
   - 次期リリースの準備（Preparation for next release）

3. **feature/**: 機能開発ブランチ（Feature development branches）
   - 個別機能の開発（Individual feature development）
   - `future`ブランチから分岐（Branched from `future`）
   - テスト合格後に`future`にマージ（Merged to `future` after tests pass）

4. **hotfix/**: 緊急修正ブランチ（Emergency fix branches）
   - 本番環境の緊急修正（Critical production fixes）
   - `main`ブランチから分岐（Branched from `main`）
   - 修正後に`main`と`future`両方にマージ（Merged to both `main` and `future`）

5. **release/**: リリース準備ブランチ（Release preparation branches）
   - リリース前の最終調整（Final adjustments before release）
   - バージョン番号更新（Version number updates）
   - リリースノート作成（Release notes creation）

### Development Workflow（開発ワークフロー）

#### Step 1: Feature Development Start（機能開発開始）

```bash
# Switch to future branch（futureブランチに切り替え）
git checkout future
git pull origin future

# Create new feature branch（新しいフィーチャーブランチを作成）
git checkout -b feature/your-feature-name

# Example feature branches:
# git checkout -b feature/person-detection-enhancement
# git checkout -b feature/position-estimation-improvement
# git checkout -b feature/action-recognition-expansion
```

#### Step 2: Development Process（開発プロセス）

```bash
# Make your changes（変更を行う）
# ... code development ...

# IMPORTANT: Update documentation with code changes
# 重要：コード変更と合わせてドキュメントを更新
# Update docs/API_Documentation.md
# Update docs/Usage_Guide.md
# Update docs/System_Architecture.md

# Stage all changes（全ての変更をステージ）
git add .

# Commit with proper message（適切なメッセージでコミット）
git commit -m "Add feature X with updated documentation

- Implement feature X in module Y
- Update API documentation for new functions
- Add usage examples and configuration options
- Update system architecture diagram

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### Step 3: Testing and Quality Assurance（テストと品質保証）

```bash
# Run all tests（全てのテストを実行）
docker-compose exec app python -m pytest

# Run code quality checks（コード品質チェックを実行）
docker-compose exec app python -m ruff format .
docker-compose exec app python -m ruff check .
docker-compose exec app python -m pyright

# Test the feature manually（機能を手動でテスト）
docker-compose exec app python main.py --debug

# Verify documentation accuracy（ドキュメントの正確性を検証）
# Check that all examples work
# Verify API documentation matches code
```

#### Step 4: Push and Pull Request（プッシュとプルリクエスト）

```bash
# Push feature branch（フィーチャーブランチをプッシュ）
git push origin feature/your-feature-name

# Create Pull Request on GitHub（GitHubでプルリクエストを作成）
# Target: future branch
# Include:
# - Feature description
# - Testing results
# - Documentation updates
# - Breaking changes (if any)
```

#### Step 5: Code Review and Merge（コードレビューとマージ）

```bash
# After PR approval, merge to future（PR承認後、futureにマージ）
git checkout future
git pull origin future
git merge --no-ff feature/your-feature-name

# Push updated future branch（更新されたfutureブランチをプッシュ）
git push origin future

# Delete feature branch（フィーチャーブランチを削除）
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

#### Step 6: Release to Main（メインへのリリース）

```bash
# When ready for release（リリース準備完了時）
git checkout main
git pull origin main

# Merge future to main（futureをmainにマージ）
git merge --no-ff future

# Tag the release（リリースにタグを付ける）
git tag -a v1.1.0 -m "Release version 1.1.0

- Enhanced person detection accuracy
- Improved position estimation algorithms
- Added new action recognition patterns
- Updated documentation and examples"

# Push main and tags（mainとタグをプッシュ）
git push origin main
git push origin --tags
```

### Feature Branch Naming Convention（フィーチャーブランチ命名規則）

Use descriptive names that clearly indicate the feature being developed:
開発中の機能を明確に示す説明的な名前を使用：

```bash
# Core functionality improvements（コア機能改善）
feature/person-detection-enhancement
feature/position-estimation-improvement
feature/action-recognition-expansion

# New major features（新しい主要機能）
feature/web-dashboard
feature/multi-camera-support
feature/face-recognition
feature/entry-exit-management

# Performance and optimization（パフォーマンスと最適化）
feature/gpu-acceleration
feature/real-time-optimization
feature/memory-usage-improvement

# Research and experimental（研究と実験的機能）
feature/deep-learning-integration
feature/3d-pose-estimation
feature/behavior-pattern-analysis

# Infrastructure and tools（インフラとツール）
feature/ci-cd-pipeline
feature/automated-testing
feature/deployment-scripts
```

### Quality Gates（品質ゲート）

Before merging any feature branch to `future`:
任意のフィーチャーブランチを`future`にマージする前に：

#### Required Tests（必須テスト）
- [ ] All unit tests pass（全ユニットテストが合格）
- [ ] Integration tests pass（統合テストが合格）
- [ ] Manual feature testing completed（手動機能テストが完了）
- [ ] Performance regression tests pass（パフォーマンス回帰テストが合格）

#### Code Quality（コード品質）
- [ ] Ruff formatting check passes（Ruffフォーマットチェックが合格）
- [ ] Ruff linting check passes（Ruffリンティングチェックが合格）
- [ ] Type checking (pyright) passes（型チェック（pyright）が合格）
- [ ] No security vulnerabilities（セキュリティ脆弱性なし）

#### Documentation Quality（ドキュメント品質）
- [ ] API documentation updated and accurate（APIドキュメントが更新され正確）
- [ ] Usage examples tested and working（使用例がテスト済みで動作）
- [ ] Architecture documentation reflects changes（アーキテクチャドキュメントが変更を反映）
- [ ] README updated if needed（必要に応じてREADMEが更新）

#### Research Validation（研究検証）
- [ ] Accuracy metrics documented（精度メトリクスが文書化）
- [ ] Performance benchmarks recorded（パフォーマンスベンチマークが記録）
- [ ] Comparison with existing methods（既存手法との比較）
- [ ] Research implications documented（研究への影響が文書化）

### Commit Message Convention（コミットメッセージ規則）

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

- For feature development commits（機能開発コミット用）:
  ```bash
  git commit -m "feature: add new person detection algorithm

  - Implement YOLO v8 integration
  - Update API documentation
  - Add configuration options
  - Include performance benchmarks
  
  🤖 Generated with [Claude Code](https://claude.ai/code)
  
  Co-Authored-By: Claude <noreply@anthropic.com>"
  ```

### Emergency Hotfix Workflow（緊急修正ワークフロー）

For critical production issues:
重要な本番環境の問題について：

```bash
# Create hotfix branch from main（mainからhotfixブランチを作成）
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue-description

# Make the fix（修正を行う）
# ... fix the issue ...

# Test the fix（修正をテスト）
# Run focused tests for the fixed issue

# Commit the fix（修正をコミット）
git commit -m "hotfix: fix critical issue X

- Fix security vulnerability in module Y
- Add regression test
- Update documentation

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push and create PR to main（プッシュしてmainへのPRを作成）
git push origin hotfix/critical-issue-description

# After merge to main, also merge to future（mainへのマージ後、futureにもマージ）
git checkout future
git pull origin future
git merge main
git push origin future
```

## Documentation Update Guidelines（ドキュメント更新ガイドライン）

### CRITICAL: Documentation Synchronization（重要：ドキュメント同期）

**When making code changes that affect the API or system behavior, you MUST update the documentation before pushing to GitHub.**
**APIやシステム動作に影響するコード変更を行う際は、GitHubにpushする前に必ずドキュメントを更新してください。**

### Required Documentation Updates（必須ドキュメント更新）

1. **API Changes（API変更時）**
   - Update `docs/API_Documentation.md` when:
     - Adding new functions, classes, or methods（新しい関数、クラス、メソッドを追加）
     - Changing function signatures（関数シグネチャを変更）
     - Modifying return values or parameters（戻り値やパラメータを変更）
     - Adding or removing modules（モジュールを追加または削除）

2. **Architecture Changes（アーキテクチャ変更時）**
   - Update `docs/System_Architecture.md` when:
     - Adding new modules or components（新しいモジュールやコンポーネントを追加）
     - Changing data flow or module interactions（データフローやモジュール間の相互作用を変更）
     - Modifying system design patterns（システム設計パターンを変更）
     - Performance characteristics change（パフォーマンス特性が変更）

3. **Usage Changes（使用方法変更時）**
   - Update `docs/Usage_Guide.md` when:
     - Adding new command-line options（新しいコマンドラインオプションを追加）
     - Changing configuration file format（設定ファイル形式を変更）
     - Modifying installation requirements（インストール要件を変更）
     - Adding new features accessible to users（ユーザーがアクセス可能な新機能を追加）

4. **Main README Updates（メインREADME更新時）**
   - Update `README.md` when:
     - Adding major new features（主要な新機能を追加）
     - Changing system requirements（システム要件を変更）
     - Modifying installation or usage instructions（インストールまたは使用方法を変更）
     - Updating project structure significantly（プロジェクト構造を大幅に更新）

### Documentation Update Process（ドキュメント更新プロセス）

#### Step 1: Code Change Analysis（ステップ1：コード変更分析）
Before making any commit, analyze your changes:
コミットする前に、変更を分析してください：

```bash
# Review what you've changed
git diff

# Check which files were modified
git status
```

#### Step 2: Identify Required Documentation Updates（ステップ2：必要なドキュメント更新の特定）
Based on your code changes, determine which documentation files need updates:
コード変更に基づいて、どのドキュメントファイルを更新する必要があるかを決定：

- **New/Modified Functions** → Update `docs/API_Documentation.md`
- **New Modules/Classes** → Update both API docs and Architecture docs
- **Configuration Changes** → Update Usage Guide and config examples
- **New Features** → Update all relevant documentation

#### Step 3: Update Documentation（ステップ3：ドキュメント更新）
Update the identified documentation files BEFORE committing:
コミットする前に特定されたドキュメントファイルを更新：

```bash
# Edit the relevant documentation files
vim docs/API_Documentation.md
vim docs/Usage_Guide.md
vim docs/System_Architecture.md

# Update README.md if needed
vim README.md

# Update configuration examples if needed
vim config.yaml
```

#### Step 4: Verify Documentation Accuracy（ステップ4：ドキュメント精度の検証）
Before committing, ensure:
コミット前に以下を確認：

- [ ] All function signatures match the actual code（全ての関数シグネチャが実際のコードと一致）
- [ ] Parameter types and descriptions are accurate（パラメータの型と説明が正確）
- [ ] Return value documentation is correct（戻り値のドキュメントが正確）
- [ ] Usage examples work with the new code（使用例が新しいコードで動作）
- [ ] Architecture diagrams reflect current design（アーキテクチャ図が現在の設計を反映）

#### Step 5: Commit Everything Together（ステップ5：全てを一緒にコミット）
Commit both code and documentation changes in the same commit:
コードとドキュメントの変更を同じコミットで行う：

```bash
# Stage all changes (code + documentation)
git add .

# Commit with descriptive message
git commit -m "Add new feature X with updated documentation

- Implement new feature X in module Y
- Update API documentation for new functions
- Add usage examples to Usage Guide
- Update system architecture diagram

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Documentation Quality Standards（ドキュメント品質基準）

1. **Accuracy（正確性）**
   - Documentation must exactly match the code（ドキュメントはコードと完全に一致する必要がある）
   - No outdated examples or incorrect signatures（古い例や不正確なシグネチャは禁止）

2. **Completeness（完全性）**
   - All public APIs must be documented（全てのパブリックAPIを文書化）
   - Include both Japanese and English descriptions（日本語と英語の両方の説明を含む）
   - Provide working examples（動作する例を提供）

3. **Clarity（明確性）**
   - Use clear, concise language（明確で簡潔な言語を使用）
   - Provide context for complex operations（複雑な操作にはコンテキストを提供）
   - Include troubleshooting information（トラブルシューティング情報を含む）

### Automated Documentation Checks（自動ドキュメントチェック）

To help maintain documentation quality, always run these checks before pushing:
ドキュメント品質を維持するため、push前に必ず以下のチェックを実行：

```bash
# Check that all public functions have docstrings
python -c "import ast; import sys; [print(f'Missing docstring: {node.name}') for file in sys.argv[1:] for node in ast.walk(ast.parse(open(file).read())) if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node) and not node.name.startswith('_')]" src/**/*.py

# Verify configuration examples are valid
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Check for broken internal links in documentation
grep -r "\[.*\](docs/" docs/ || echo "No internal links found"
```

### Pre-Push Checklist（Push前チェックリスト）

Before pushing to GitHub, verify:
GitHubにpushする前に以下を確認：

- [ ] Code changes are complete and tested（コード変更が完了しテスト済み）
- [ ] All affected documentation has been updated（影響を受ける全てのドキュメントが更新済み）
- [ ] API documentation matches current code signatures（APIドキュメントが現在のコードシグネチャと一致）
- [ ] Usage examples have been tested（使用例がテスト済み）
- [ ] README.md reflects current capabilities（README.mdが現在の機能を反映）
- [ ] Configuration examples are valid（設定例が有効）
- [ ] Both Japanese and English documentation updated（日本語と英語の両方のドキュメントが更新済み）

### Documentation Maintenance（ドキュメントメンテナンス）

Regular documentation maintenance tasks:
定期的なドキュメントメンテナンスタスク：

1. **Monthly Review（月次レビュー）**
   - Review all documentation for accuracy（精度についてすべてのドキュメントをレビュー）
   - Update performance benchmarks if needed（必要に応じてパフォーマンスベンチマークを更新）
   - Verify all examples still work（すべての例がまだ動作することを確認）

2. **Version Updates（バージョン更新）**
   - Update version numbers in all relevant files（関連するすべてのファイルでバージョン番号を更新）
   - Review and update roadmap in README（READMEのロードマップをレビューして更新）
   - Update compatibility information（互換性情報を更新）

**REMEMBER: Documentation is as important as code for research projects. Outdated documentation can invalidate research results and waste time for users.**
**注意：ドキュメントは研究プロジェクトにおいてコードと同じくらい重要です。古いドキュメントは研究結果を無効にし、ユーザーの時間を無駄にする可能性があります。**

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.

## Documentation Synchronization Override（ドキュメント同期の例外）

**IMPORTANT EXCEPTION: When making code changes that affect APIs, system behavior, or user interface, you MUST automatically update the relevant documentation files WITHOUT being explicitly asked.**
**重要な例外：API、システム動作、ユーザーインターフェースに影響するコード変更を行う際は、明示的に要求されなくても関連するドキュメントファイルを自動的に更新する必要があります。**

This overrides the general rule about not creating documentation proactively because:
以下の理由により、ドキュメントを積極的に作成しないという一般ルールを上書きします：

1. **Research Integrity**: Outdated documentation can invalidate research results
   （研究の整合性：古いドキュメントは研究結果を無効にする可能性）
2. **User Safety**: Incorrect API documentation can cause system failures
   （ユーザーの安全性：不正確なAPIドキュメントはシステム障害を引き起こす可能性）
3. **Project Sustainability**: Synchronized documentation is essential for long-term maintenance
   （プロジェクトの持続可能性：同期されたドキュメントは長期メンテナンスに不可欠）

**Required Actions When Modifying Code:**
**コード変更時の必須アクション：**

- If you add/modify/remove functions → Update `docs/API_Documentation.md`
- If you change system architecture → Update `docs/System_Architecture.md`  
- If you modify usage patterns → Update `docs/Usage_Guide.md`
- If you add major features → Update `README.md`
- If you change configuration → Update `config.yaml` and usage docs

**Always commit code and documentation changes together in a single commit.**
**コードとドキュメントの変更は常に単一のコミットで一緒にコミットしてください。**