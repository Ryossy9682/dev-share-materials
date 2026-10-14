---
name: gdw-design
description: "承認済み要件から詳細設計を作るとき、または設計指摘へ対応するときに使う。"
---

# gdw-design

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.gemini/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：coverage](../../workflow/references/coverage.md)

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：requirements.md, approval.md, investigation.md, estimates.md; design-review.md（差し戻し時）。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：design.md, design/<対象名>.md, test-cases.md, coverage-scope.md, traceability.md。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

1. 要件承認と調査の鮮度を確認する。未承認の業務挙動を設計に追加しない。
2. design.mdを入口に、変更ファイル単位でdesign/<対象名>.mdを作る。変更理由、REQ/AC、責務、シンボル/引数/型/戻り値、前後条件、処理、例外、データ/API、依存、互換性、権限、並行処理、移行・復旧を必要な範囲で具体化する。
3. 実装時に重要な仕様判断を残さない。既存の単純な構成・ライブラリを優先し、追加依存には必要性を記録する。
4. この時点でtest-cases.mdへUT/結合/動作確認のケースと入力・期待結果・観点・対応要件を設計する。テストコードは実装後に作る。
5. coverage-scope.mdで追加変更処理と分岐計測方法を定義し、traceability.mdで全ACから設計・予定テストを結ぶ。
6. 見積もりを更新し、固定した成果物ハッシュをhandoff.mdにまとめて設計独立レビューへ渡す。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.gemini/agents/gdw-design.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
