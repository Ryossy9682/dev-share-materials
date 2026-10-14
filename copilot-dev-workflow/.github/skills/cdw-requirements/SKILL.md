---
name: cdw-requirements
description: "案件の要件定義、受入条件の確定、要件変更時に使う。一問一答で不足情報を確認し、人の承認を取得する。"
---

# cdw-requirements

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.github/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：stages](../../workflow/references/stages.md)

初回のブランチ確定前は、model-policy.mdに従って親が保存した受付ルートのrequest.mdを固定入力として読む。

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：branch.md, environment.md（初回準備後）; investigation.md, estimates.md（承認時）; requirements.md（再開時）。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：requirements.md, branch.md（初回）, approval.md。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

0. 初回は[ブランチ準備](../../workflow/references/branching.md)を実行し、ブランチ名の決定・最新develop取得・作業ブランチ作成・案件ルート作成を完了する。続いてbootstrapを実行してenvironment.mdを保存してから以下へ進む。再開時は再作成しない。
1. 依頼、既存の要件定義の枠、関連仕様を読む。枠が未共有ならrequirements.mdひな型を暫定利用し、後日の項目対応を残す。
2. 目的、利用者、対象/対象外、現行挙動と期待挙動、制約、データ/権限、非機能、互換性、受入条件、リリース制約からこの案件に必要なものを選ぶ。既知事項を再質問しない。
3. 最も影響が大きい未決事項を一問だけ提示し回答を待つ。必要なら選択肢と推奨理由を短く添える。複数の小問を一問へ詰め込まない。利用可能な質問ツールがなければ通常の対話を使う。
4. REQ-001とAC-001等の安定IDで、入力条件・操作・観測可能な期待結果を記録する。曖昧な「問題なく動く」で終わらせない。優先度と出典、未決、前提を分ける。
5. 草案ができたらinvestigate/estimateへ渡し、コードと食い違う点だけ一問ずつ確認する。新規開発ならコード未存在とスキャフォールド方針を記録する。
6. 要件・受入条件・対象外・未決解消・C/B/A見積もりを提示し、要件版への人の明示承認をapproval.mdに保存する。未承認はAWAITING_APPROVAL。後で要件が変われば同じゲートに戻す。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.github/agents/cdw-requirements.agent.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
