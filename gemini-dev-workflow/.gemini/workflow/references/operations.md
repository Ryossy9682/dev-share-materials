# 運用機能の入口

既存工程に追加する固定入力。モデルは既存agentsのmodelを使う。doctor・資料照合・品質判定・実機試験の評価はcheck担当（高性能）、設定・更新・画面生成・実機試験の実行はsetup/start/status等の既存軽量担当へ委任する。新しいモデル正本を作らない。

| タイミング | 読む規約 | 案件の読込ファイル | 更新ファイル |
|---|---|---|---|
| setup・開始・再開・ホスト更新 | ops-doctor.md | evidence/host-observations.json、観測ログ、project/profile.json、agents全定義 | doctor.md、evidence/doctor.json |
| 配布版・モデル更新 | ops-evaluation.md | 評価用README.md、evaluation.json、各試験の案件MD | evaluations/以下、evaluation-result.json |
| 初期設定・セッション切替 | ops-hooks.md | 担当別hook-config.json、gate.json、承認証跡 | hooks.md、担当別設定 |
| 導入・更新・復旧 | ops-update.md | 配布版、導入版、workflow-install.json、外部journal.json | update.md、導入状態、復旧台帳 |
| 調査・再開・資料変更 | ops-sources.md | sources.lock.json、evidence/source-observations.json、取得原本、project/profile.json | sources.md、sources/、gate.json |
| 状況表示 | ops-dashboard.md | gate.json、evidence/operations-result.json、issues.md、estimates.md、metrics.json | dashboard.html |
| check・advance・CI | ops-quality.md | ops.json、Git基準SHA、品質対象ファイル、evidence/quality-approval.json | quality.md、operations.md、evidence/operations-result.json |

新規bootstrapで既存runtime init後にops initを実行する。baseはbranch.mdで確定した取得SHAをそのまま指定。旧案件もops initし、未取得証跡は未確認のまま止める。既存runtimeのcheck/advance自体が運用検査を必須実行するため、旧コマンドの直接呼出しでも省略されない。

```sh
python .gemini/workflow/runtime/ops.py --case /tmp/REPO/feature.xxx --base BASE_SHA init
python .gemini/workflow/runtime/ops.py --case /tmp/REPO/feature.xxx --base BASE_SHA gate
python .gemini/workflow/runtime/ops.py --case /tmp/REPO/feature.xxx --base BASE_SHA advance
```

`BASE_SHA`等は実値に置き換える。基準をHEADで追認しない。工程MDは最新結果を更新し操作履歴を追記する。元の実行ログは改変しない。失敗時は停止理由を該当工程MDとissues.mdへ追記して親に返す。
