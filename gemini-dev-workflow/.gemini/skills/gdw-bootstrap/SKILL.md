---
name: gdw-bootstrap
description: "クローン直後のワークフロー初期設定（configure）、導入先で初めて開発を開始する場合、または実行環境が変わった場合の環境・利用機能調査に使う。"
---

# gdw-bootstrap

## 初期設定（configure）

初期設定の依頼またはproject/profile.jsonがREADYでない場合は、[初期設定規約](../../workflow/references/project-setup.md)だけに従って初期設定を行い、完了で停止する。以下の案件入力・工程出力はconfigureモードには適用しない。案件用state.jsonは作成しない。

## 入力と参照

案件ルートは`/tmp/<repo-id>/<branch>/`。入力・終了条件は工程表に従います。開始時に次の資料だけを読み、必要なテンプレートは`.gemini/workflow/templates/`から選びます。相対参照はこのスキルファイル基準です。
- [共通規約：contract](../../workflow/references/contract.md)
- [共通規約：compatibility](../../workflow/references/compatibility.md)

## 固定の案件入力と出力

全工程共通：00-index.mdとstate.jsonを実ファイルから読む。新規開始のworkflowとrequirements-setupだけは、まだ存在しないこの2ファイルの読込を免除し、初回準備で作成する。以下のパスは案件ルート基準。初回作成担当のみ未作成を許容し、後続の必須入力が無ければ停止する。
- 固定の案件入力：branch.md, requirements.md（初期メタデータ）。
- モードにかかわらず、下記の更新対象の正本が既に存在する場合は必ず読み、最新本文と履歴を保持する。bootstrap以外はenvironment.mdも読む（requirements初回準備・新規workflowのbootstrap前だけは未作成を許容）。
- 更新する正本：environment.md。
- [保存・受け渡し規約](../../workflow/references/artifacts.md)に従い、同じ工程MDの最新本文を更新し、下部の更新履歴へ追記する。本文の会話引継ぎは禁止。

## 手順

1. environment.mdひな型を使い、Gitルート、既存変更、OS/シェル、Gemini契約・版、IDE拡張版、ツール一覧を確認する。秘密値は読込/出力しない。
2. プロジェクトのREADME、依存定義、既存のGEMINI.md、CI、テスト・デプロイ設定を必要な範囲だけ読む。既存規約を優先し、矛盾は記録する。
3. 言語、実行/ビルド/lint/UT/結合/カバレッジ/動作確認コマンドと作業ディレクトリ、テスト用データ、外部連携を導入先で具体化する。架空のコマンドを埋めない。
4. ネイティブスキル、独立サブエージェント、ファイル明示読込を確認する。別セッションによるレビューの引継ぎ方法を確定する。
5. /tmpの書込・保持条件とチェックポイント保存先を確認する。非本番の検証環境、CIによる自動デプロイ、利用権限を確認する。起動不可ならBLOCKED、可能なら要件定義へ進む。

## 出力

成果物を案件ルートへ保存し、state.jsonのstage/status/next_action、成果物ハッシュ、対応要件、問題台帳を更新してください。レビュー工程では固定された各工程のレビューMDに原文と再確認履歴を残します。実行権限のない書込は親または別の許可された工程へ引き継ぎます。

## 機械検査との接続

案件モードでは[機械検査・復旧規約](../../workflow/references/runtime.md)と案件ルートのgate.jsonを固定入力として読む。init前の初回準備とbootstrapのconfigureは除外する。工程完了の進行状態はランタイムのcheck/advanceで確定し、手編集で合格や次工程へ変更しない。実行ログ・レビュー・承認の元資料を必ず紐付ける。

## 実行モデル

[モデル割当規約](../../workflow/references/model-policy.md)を固定入力として読み、`.gemini/agents/gdw-bootstrap.md`のmodelを使用する担当へ実行を渡す。既に対応担当・指定モデルで実行中なら再委任しない。工程移動は親へ返し、別の担当モデルのまま続行しない。

## 運用検査

[運用機能の入口](../../workflow/references/operations.md)の工程表で、この担当が読む規約と固定入力を確認する。必須証跡が無い場合は停止し、親へ不足を返す。
