# 工程・スキル・ファイル詳細

[READMEへ戻る](../README.md)

固定入力、出力、共通規約を省略せず掲載しています。

案件開始前にcdw-bootstrapのconfigureモードを実行します。全スキルに追加された可変領域の固定入力、初期設定の全出力は[初期設定規約](../.github/workflow/references/project-setup.md)に省略なく記載しています。Notion使用時の固定参照は[Notionセットアップ](../.github/workflow/references/notion-setup.md)で、取得資料の具体的パスはinventory.mdへ全件記録します。全案件工程は[機械検査・復旧規約](../.github/workflow/references/runtime.md)とgate.jsonも固定入力に追加します。工程進行は共通ランタイムで行います。以下は初期設定完了後の案件工程です。

案件ファイルは`/tmp/<repo-id>/<branch>/`からの相対パス、スキルと共通規約はリポジトリルートからの相対パスです。`<対象名>`は導入先で確定し、`design.md`に具体的な全ファイル名を列挙します。実装・テストコードの具体的パスも導入先で確定し、設計・実装記録・テスト記録に列挙します。

実行順は、requirementsの初回準備→bootstrap→requirementsの要件草案→investigate→estimate→requirementsの要件承認→design→review-design→implement→review-implementation→tests→review-tests→verify→deliver→releaseです。workflowが各工程の進行を管理します。

| 全スキルに適用する読込・更新 | ファイルと条件 |
|---|---|
| 起動時の共通指示 | `.github/copilot-instructions.md`、実行するスキルの`SKILL.md` |
| 共通入力 | `00-index.md`、`state.json`。新規workflowとrequirements初回準備だけは作成前の不存在を許容 |
| 環境入力 | `environment.md`。bootstrapが作成。新規workflowとrequirements初回準備ではbootstrap前の不存在を許容 |
| 関連する承認・指摘 | `approval.md`、`issues.md`の関連ID。要件版・対象SHAとの一致を確認 |
| 更新前の入力 | 各工程の更新対象が既に存在する場合、その正本の本文と更新履歴を読む。初回・再開・差し戻しを問わない |
| 共通更新 | `00-index.md`、`state.json`。指摘発生時は`issues.md`、判断記録は`decisions.md`。独立レビュー準備時は`handoff.md` |
| 初回に初期化 | `branch.md`、`requirements.md`、`00-index.md`、`state.json`、`issues.md`、`approval.md`、`decisions.md`、`resume.md` |

各工程の入力は上記共通入力への追加です。「要件一式」「設計一式」などの略記を使わず、固定ファイル名を記載します。条件付きファイルは条件が成立したときに読みます。

## 工程別の読込・出力

### 全体：進行・再開管理

定義：`.github/skills/cdw-workflow/SKILL.md`

**読み込む案件ファイル**

- `00-index.md`
- `state.json`

**作成・更新するファイル**

- `resume.md`

### 初回準備：ブランチ準備・要件定義・要件承認

定義：`.github/skills/cdw-requirements/SKILL.md`

**読み込む案件ファイル**

- `branch.md`
- `environment.md`（初回準備後）
- `investigation.md`（承認時）
- `estimates.md`（承認時）
- `requirements.md`（再開時）
- ユーザーが共有した要件定義の枠（提供時。ファイル名は導入先で記録）

**作成・更新するファイル**

- `requirements.md`
- `branch.md`（初回）
- `approval.md`

### 0：環境調査

定義：`.github/skills/cdw-bootstrap/SKILL.md`

**読み込む案件ファイル**

- `branch.md`
- `requirements.md`（初期メタデータ）

**作成・更新するファイル**

- `environment.md`

### 2：仕様理解・影響調査

定義：`.github/skills/cdw-investigate/SKILL.md`

**読み込む案件ファイル**

- `branch.md`
- `environment.md`
- `requirements.md`
- 対象コード・既存テスト（具体的パスは導入先の調査/設計記録に列挙）

**作成・更新するファイル**

- `investigation.md`

### 3：工数見積もり

定義：`.github/skills/cdw-estimate/SKILL.md`

**読み込む案件ファイル**

- `branch.md`
- `requirements.md`
- `investigation.md`
- `design.md`（設計後の更新時）

**作成・更新するファイル**

- `estimates.md`

### 5：詳細設計・テストケース設計

定義：`.github/skills/cdw-design/SKILL.md`

**読み込む案件ファイル**

- `requirements.md`
- `approval.md`
- `investigation.md`
- `estimates.md`
- `design-review.md`（差し戻し時）

**作成・更新するファイル**

- `design.md`
- `design/<対象名>.md`
- `estimates.md`（設計による見積もり更新時）
- `test-cases.md`
- `coverage-scope.md`
- `traceability.md`

### 6：詳細設計の独立レビュー

定義：`.github/skills/cdw-review-design/SKILL.md`

**読み込む案件ファイル**

- `handoff.md`
- `requirements.md`
- `approval.md`
- `investigation.md`
- `design.md`
- `design/<対象名>.md`（design.mdに列挙された全ファイル）
- `test-cases.md`
- `coverage-scope.md`
- `traceability.md`
- 対象コード・既存テスト（具体的パスは導入先の調査/設計記録に列挙）

**作成・更新するファイル**

- `design-review.md`

### 7：実装

定義：`.github/skills/cdw-implement/SKILL.md`

**読み込む案件ファイル**

- `branch.md`
- `requirements.md`
- `approval.md`
- `design.md`
- `design/<対象名>.md`（design.mdに列挙された全ファイル）
- `design-review.md`
- `implementation-review.md`（差し戻し時）

**作成・更新するファイル**

- `implementation.md`
- `traceability.md`
- 実装コード（design.mdに列挙した対象パス）

### 8：実装の独立レビュー

定義：`.github/skills/cdw-review-implementation/SKILL.md`

**読み込む案件ファイル**

- `handoff.md`
- `requirements.md`
- `approval.md`
- `design.md`
- `design/<対象名>.md`（design.mdに列挙された全ファイル）
- `implementation.md`
- `traceability.md`
- 対象コード・既存テスト（具体的パスは導入先の調査/設計記録に列挙）

**作成・更新するファイル**

- `implementation-review.md`

### 9：UT・結合テスト実装と実行

定義：`.github/skills/cdw-tests/SKILL.md`

**読み込む案件ファイル**

- `requirements.md`
- `design.md`
- `test-cases.md`
- `implementation.md`
- `implementation-review.md`
- `coverage-scope.md`
- `test-review.md`（差し戻し時）

**作成・更新するファイル**

- `tests.md`
- `test-cases.md`
- `coverage-scope.md`
- `traceability.md`
- UT/結合テストコード（test-cases.mdに対応する対象パス）
- evidence/<実行ID>のログ・計測レポート

### 10：テストの独立レビュー

定義：`.github/skills/cdw-review-tests/SKILL.md`

**読み込む案件ファイル**

- `handoff.md`
- `requirements.md`
- `design.md`
- `implementation.md`
- `test-cases.md`
- `tests.md`
- `coverage-scope.md`
- `traceability.md`
- 対象コード・既存テスト（具体的パスは導入先の調査/設計記録に列挙）

**作成・更新するファイル**

- `test-review.md`

### 11：動作確認

定義：`.github/skills/cdw-verify/SKILL.md`

**読み込む案件ファイル**

- `environment.md`
- `requirements.md`
- `test-cases.md`
- `tests.md`
- `test-review.md`
- `implementation-review.md`

**作成・更新するファイル**

- `verification.md`
- evidence/<実行ID>の動作確認証跡

### 12：コミット・PR・添付資料作成

定義：`.github/skills/cdw-deliver/SKILL.md`

**読み込む案件ファイル**

- `branch.md`
- `requirements.md`
- `approval.md`
- `estimates.md`
- `design.md`
- `design-review.md`
- `implementation.md`
- `implementation-review.md`
- `tests.md`
- `test-review.md`
- `verification.md`
- `traceability.md`
- `issues.md`

**作成・更新するファイル**

- `delivery.md`
- `release.md`（準備案）
- `pr/pr-summary.md`
- `pr/pr-report.md`
- `pr/feature.xxx-review.zip`
- pr/stages/の可搬MD
- pr/evidence/の証跡
- `pr/manifest.json`

### 13：リリース準備・承認後の反映

定義：`.github/skills/cdw-release/SKILL.md`

**読み込む案件ファイル**

- `branch.md`
- `approval.md`
- `delivery.md`
- `release.md`
- `verification.md`
- `design-review.md`
- `implementation-review.md`
- `test-review.md`
- `issues.md`

**作成・更新するファイル**

- `release.md`
- `approval.md`

requirementsは初回準備・要件草案（工程1）・要件承認（工程4）で同じスキルを使用します。estimates.mdの列順はC（AIなし人的工数）→B（Copilot活用時の所要時間）→A（Copilot活用時の人的工数）です。

## 独立レビューの基準と対象

以下に加え、直前の共通入力と各スキルの固定入力を読みます。`handoff.md`は対象版・ファイルパス・証跡を特定するための管理ファイルです。

| 独立レビュー | 基準として照合する案件ファイル | レビュー対象・直接確認する実物 | 判定の保存先 |
|---|---|---|---|
| 詳細設計 | `requirements.md`、`approval.md`、`investigation.md` | `design.md`、`design/<対象名>.md`、`test-cases.md`、`coverage-scope.md`、`traceability.md`、参照先の実コード | `design-review.md` |
| 実装 | `requirements.md`、`approval.md`、`design.md`、`design/<対象名>.md` | 実装コード、`implementation.md`、`traceability.md`。具体的コードパスは設計・実装記録で特定 | `implementation-review.md` |
| テスト | `requirements.md`、`design.md`、`implementation.md`、関連承認を記録した`approval.md` | UT/結合テストコード、実装コード、`test-cases.md`、`tests.md`、`coverage-scope.md`、`traceability.md`、`evidence/`内の対象ログ・計測レポート | `test-review.md` |

## 各スキルが読む共通規約の全パス

| スキル定義ファイル | 共通規約ファイル |
|---|---|
| `.github/skills/cdw-workflow/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/stages.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-requirements/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/stages.md`, `.github/workflow/references/artifacts.md`, `.github/workflow/references/branching.md` |
| `.github/skills/cdw-bootstrap/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/compatibility.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-investigate/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-estimate/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/estimation.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-design/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/coverage.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-review-design/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/review.md`, `.github/workflow/references/coverage.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-implement/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/release.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-review-implementation/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/review.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-tests/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/coverage.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-review-tests/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/review.md`, `.github/workflow/references/coverage.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-verify/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/release.md`, `.github/workflow/references/artifacts.md` |
| `.github/skills/cdw-deliver/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/release.md`, `.github/workflow/references/artifacts.md`, `.github/workflow/references/pr-artifacts.md` |
| `.github/skills/cdw-release/SKILL.md` | `.github/workflow/references/contract.md`, `.github/workflow/references/release.md`, `.github/workflow/references/artifacts.md` |

## PR添付用の出力ファイル

| 案件ディレクトリからのパス | 内容 |
|---|---|
| `pr/pr-summary.md` | PR本文用の変更目的・概要・検証・制限 |
| `pr/pr-report.md` | 変更範囲、要件と実装の対応、検証、リリース準備、工程資料への案内 |
| `pr/stages/` | 工程MDとdesign/詳細の可搬コピー。具体的なコピー一覧をmanifest.jsonへ記録 |
| `pr/evidence/` | 添付する実行ログ・計測証拠。具体的なファイル一覧をmanifest.jsonへ記録 |
| `pr/manifest.json` | branch/base/head SHA、要件版、生成日時、添付ファイルのSHA-256 |
| `pr/feature.xxx-review.zip` | 報告書・工程資料・証跡をまとめた添付ZIP |

添付ZIPには`00-index.md`、`state.json`、`handoff.md`、`resume.md`を含めません。`delivery.md`の可搬コピーからは添付管理情報を除外します。詳細は`.github/workflow/references/pr-artifacts.md`に従います。


## 操作入口スキルの定義ファイル

| コマンド | 定義ファイル |
|---|---|
| `/cdw-setup` | `.github/skills/cdw-setup/SKILL.md` |
| `/cdw-start` | `.github/skills/cdw-start/SKILL.md` |
| `/cdw-status` | `.github/skills/cdw-status/SKILL.md` |
| `/cdw-resume` | `.github/skills/cdw-resume/SKILL.md` |
| `/cdw-check` | `.github/skills/cdw-check/SKILL.md` |
| `/cdw-impact` | `.github/skills/cdw-impact/SKILL.md` |
| `/cdw-mutate` | `.github/skills/cdw-mutate/SKILL.md` |

全コマンドが.github/copilot-instructions.mdを読みます。setupはbootstrap、startはworkflow、その他はruntime.mdの手順を読みます。本文をコマンド引数へ引き継ぎません。

機械検査で追加する全ファイルは[検査用ファイル一覧](../.github/workflow/references/runtime.md#検査用ファイル一覧)に記載しています。

全工程は`.github/workflow/references/model-policy.md`と対応する`.github/agents/`の定義を固定入力として読みます。21担当の省略なしのパスは[モデル定義一覧](../.github/workflow/references/model-policy.md#全担当の割当)に掲載しています。

## 運用機能の固定入力・出力

[7機能の省略なし一覧](../.github/workflow/references/operations.md)で、各規約ファイル・案件入力・更新先を確認してください。担当モデルは既存21定義を使用します。
