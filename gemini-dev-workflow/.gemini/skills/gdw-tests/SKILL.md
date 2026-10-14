---
name: gdw-tests
description: "実装レビュー後のUT・結合テストコード作成、またはケース/テスト実装の不足修正に使う。"
---

# gdw-tests

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.gemini/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：coverage](../../workflow/references/coverage.md)

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：requirements.md, design.md, test-cases.md, implementation.md, implementation-review.md, coverage-scope.md; test-review.md（差し戻し時）。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：tests.md, test-cases.md, coverage-scope.md, traceability.md。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

1. 実装レビューPASSと設計済みtest-cases.mdを確認し、UTと結合テストを分けて実装する。
2. UTは外部境界だけを必要に応じてモック化し、対象ロジックをモックしない。結合テストは検証対象となる実際のコンポーネント間連携を動かす。すべての接続先をモックしたものを結合の証拠にしない。
3. 結合テストには専用のデータ/環境と後始末を用意する。本番データを破壊しない。外部サービスの実試験ができなければ未検証として止める。
4. UT単独の行・分岐レポートを出力し、固定した差分対象にcoverage規約を適用する。ケースごとの実行結果、アサーション、失敗、再現方法を保存する。
5. 新しいユースケースを見つけたらACに対する不足か新要件かを区別し、testsまたはrequirementsへ渡す。実装が誤りなら期待値を実装に合わせずimplementへ戻す。
6. 実装・ケース・計測証拠を固定して独立レビューへ渡す。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.gemini/agents/gdw-tests.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
