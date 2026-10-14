---
name: cdw-deliver
description: "検証済み変更をGitコミット・PRとリリース準備資料にまとめるときに使う。マージはしない。"
---

# cdw-deliver

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.github/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：release](../../workflow/references/release.md)

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：branch.md, requirements.md, approval.md, estimates.md, design.md, design-review.md, implementation.md, implementation-review.md, tests.md, test-review.md, verification.md, traceability.md, issues.md。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：delivery.md, release.md（準備案）, pr/pr-summary.md, pr/pr-report.md, pr/feature.xxx-review.zip。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

1. 全レビュー、要件承認、テスト・動作確認が現行対象に一致すること、未解決問題がないことを確認する。
2. 作業ブランチに担当ファイルだけをコミットし、差分と証拠をPR本文にまとめる。push/PRの自動本番反映トリガーがないことを確認してから実行する。
3. 先にrelease.mdの準備案とdelivery.mdを更新し、本番/外部マージ待ちの現状を反映する。その後、[PR添付仕様](../../workflow/references/pr-artifacts.md)に従ってPR向けMarkdownとZIPを生成し、base=develop/head=作業ブランチを確認する。PRには問題・変更後の挙動・要件対応・検証・制限・復旧方針を記載する。マージ、自動マージ設定は絶対にしない。
4. PR作成・添付の結果をdelivery.mdに更新する。技術的内容が変わったら添付を再生成する。添付URL・ZIPハッシュ等の管理情報だけの追記は再生成対象にしない。外部マージが必要なら待機する。対象変更後は証跡を更新し、releaseへ渡す。ローカル納品だけが依頼範囲ならPRを勝手に作成しない。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.github/agents/cdw-deliver.agent.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
