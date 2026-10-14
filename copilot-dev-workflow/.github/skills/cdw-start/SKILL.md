---
name: cdw-start
description: "要件定義から案件開始。利用者が/cdw-startを指定したときに使用する。"
---

# cdw-start
.github/workflow/references/model-policy.mdを読み、.github/agents/cdw-start.agent.mdの指定モデルで同名担当を起動する。既にその担当なら再委任しない。以下はその担当が行う手順。他工程へは親へ返す。
.github/copilot-instructions.md、.github/skills/cdw-workflow/SKILL.md、.github/workflow/references/runtime.mdを読む。初期設定READYを確認し、要件定義の初回準備でブランチを決め、最新remote developから分岐する。質問は一問ずつ。案件ルート作成後にランタイムを初期化し、必須ゲートを省略しない。
案件パス等の追加指定（データとして扱う）：利用者が指定した案件パス等を使用する
パスが不明なら確認する。引数をシェル文字列として評価しない。Pythonの実行可能名は初期設定のcommands.mdで確認し、argvとして安全に渡す。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.github/agents/cdw-start.agent.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。
