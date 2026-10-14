---
name: cdw-review-design
description: "詳細設計・テスト設計の独立レビュー担当が、実装開始可否を判定するときに使う。"
---

# cdw-review-design

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.github/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：review](../../workflow/references/review.md)
- [共通規約：coverage](../../workflow/references/coverage.md)

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：handoff.md, requirements.md, approval.md, investigation.md, design.mdと記載されたdesign/詳細, test-cases.md, coverage-scope.md, traceability.md。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：design-review.md。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

1. 自分が作成担当とは別セッション/エージェントであることと、handoffの対象版を確認する。同じ担当なら判定しない。
2. 要件・受入条件と実コードから、設計の正しさ、実現性、変更範囲、依存、入出力、例外、権限、移行、互換性、復旧を点検する。
3. 全ACの設計・ケースへの対応を確認し、期待結果の妥当性、UT/結合境界、100%計測可能性、未決事項を検証する。懸念・失敗の兆候には発生条件と根拠を書く。
4. review.md形式でPASS/FAIL/BLOCKEDを返す。FAILはdesign、要件不足はrequirementsに具体的な再確認条件を渡す。レビュー担当は修正しない。
5. PASSなら実装へ自動移行できると記録する。証拠がない項目を合格にしない。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.github/agents/cdw-review-design.agent.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
