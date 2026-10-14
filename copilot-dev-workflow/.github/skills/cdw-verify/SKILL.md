---
name: cdw-verify
description: "UTと結合検証の合格後、画面・API・バッチ等の主要ユースケースを実行確認するときに使う。"
---

# cdw-verify

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.github/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：release](../../workflow/references/release.md)

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：environment.md, requirements.md, test-cases.md, tests.md, test-review.md, implementation-review.md。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：verification.md。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

1. 検証対象のコミット/ビルド・環境・テストデータ・アカウントを確認する。UI/API/バッチの該当ユースケースをtest-cases.mdから選ぶ。
2. 起動、入力、出力、保存、再読込、権限、異常、既存主要機能の回帰を実環境で確認する。ブラウザが必要なら利用可能な正規ツールで操作する。
3. verification.mdへケース、期待/実測、ログ、必要な画面証跡、後始末を記録する。手順書だけを実施済みとしない。
4. セキュリティ/性能/アクセシビリティ等は要件に応じ実測する。適用外には根拠を記録し、必要な環境がなければBLOCKED。
5. 全対象合格ならdeliverへ。不合格は根本原因へ戻し、修正された対象の独立レビューと影響テストを再実行する。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.github/agents/cdw-verify.agent.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
