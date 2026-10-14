---
name: gdw-review-tests
description: "UT・結合テストと計測証拠の独立レビュー担当が、ケース網羅性と100%条件を判定するときに使う。"
---

# gdw-review-tests

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.gemini/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：review](../../workflow/references/review.md)
- [共通規約：coverage](../../workflow/references/coverage.md)

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：handoff.md, requirements.md, design.md, implementation.md, test-cases.md, tests.md, coverage-scope.md, traceability.md。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：test-review.md。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

1. 要件/AC、設計、実装、全ケースを直接照合し、未対応ACや失敗経路を探す。担当者のケース一覧だけで判断しない。
2. 対象ロジックの過剰モック、実装の丸写し、無意味なassert、skip、未実行ファイル、除外設定、ソースマップ、丸め、結合結果の混入を点検する。
3. coverage-scope.mdとUT単独レポートから追加変更処理の全対象行・分岐が実行されていることを確認する。計測不能/ログ不足はBLOCKED。
4. 結合テストが対象境界を実際に通ること、失敗/データ整合/後始末を検証することを確認する。必要なら利用可能な権限で再実行し、読取専用ならログと再実行依頼を返す。
5. 不足はtests、実装不良はimplement、仕様不足はdesign/requirementsへ渡す。UT100%・ケース網羅・結合合格の全条件を満たしたときだけPASS。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.gemini/agents/gdw-review-tests.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
