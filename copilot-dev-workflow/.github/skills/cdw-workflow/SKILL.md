---
name: cdw-workflow
description: "開発の開始・再開・次工程への移動を依頼されたときに使うCopilot用統括手順。個別工程の代わりに全資料を一括読込しない。"
---

# cdw-workflow

## 開始前の初期設定確認

[初期設定規約](../../workflow/references/project-setup.md)とproject/profile.jsonを確認する。未設定・STALE・対象不一致ならbootstrapのconfigureモードへ移り、初期設定完了で停止する。READYの場合だけ以下の案件手順を適用する。

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.github/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：stages](../../workflow/references/stages.md)

初回のブランチ確定前は、model-policy.mdに従って親が保存した受付ルートのrequest.mdを固定入力として読む。

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：00-index.md, state.json。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：resume.md。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

1. 新規案件はrequirementsの初回準備へ進み、feature.xxxブランチと案件ルートを確定する。再開は渡された案件ルートの00-index.md/state.jsonを読み、ブランチを照合する。
2. 工程表に従い現在工程のSKILL.mdと必要な参照資料だけを読む。スキル機能があれば有効化し、なければファイルを明示読込する。
3. 入力・承認・証跡の鮮度を確認し、工程を実施する。PASSのみ次へ進む。テンプレートを先に全量読込しない。
4. 指摘をissues.mdへ記録し、根本原因の工程へ差し戻す。独立レビューの不在、未検証、3回未解決は停止する。
5. 次のスキルにはスキル名・案件ルート絶対パス・モードだけを渡し、本文や要約をコピーしない。完了工程・次の作業・参照先・担当ロックをstate.jsonへ記録し、resume.mdを更新する。長いセッションは原資料への参照を残して新しいセッションへ引き継ぐ。
6. 本番反映前の人の承認、外部マージ待ちを守る。マージしない。ユーザーが指定した到達点で終了し、それ以降の副作用を起こさない。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

init後の進行はgate.jsonが正本。state.jsonの旧stage/status/next_actionは参照せず、cdw.py statusから次の操作を決める。開始・復元後にはgitの実ブランチとbranch.mdのbase/headを照合する。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.github/agents/cdw-workflow.agent.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
