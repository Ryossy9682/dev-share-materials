---
name: gdw-release
description: "本番リリース準備、対象を限定した人の承認後の反映、事前承認条件に基づくロールバックに使う。"
---

# gdw-release

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.gemini/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：release](../../workflow/references/release.md)

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：branch.md, approval.md, delivery.md, release.md, verification.md, design-review.md, implementation-review.md, test-review.md, issues.md。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：release.md, approval.md。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

1. release.mdの事前条件・対象SHA/digest・環境・復旧手順と、現行の全ゲートPASSを確認する。未検証があれば準備完了にしない。
2. 人が判断できる計画・証跡を提示し、AWAITING_APPROVALで本番承認を待つ。実装開始の承認を流用しない。
3. 承認対象と実際の対象が一致し、外部で必要なマージが完了していれば承認された手順で反映する。自分ではマージしない。
4. 本番の疎通・主要ユースケース・メトリクスを指定期間確認し、結果を記録する。事前承認条件の異常なら承認された手順で自動ロールバックし復旧を確認する。
5. 条件外の異常/復旧失敗は停止・報告する。実施・未実施、環境、反映版、復旧状態を明確にして終了する。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.gemini/agents/gdw-release.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

本番操作前のゲート判定はcheck担当、反映後の動作確認はverify担当へ親を通して委任する。release担当は人の承認済み操作だけを実行する。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
