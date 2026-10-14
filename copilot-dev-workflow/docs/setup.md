# 導入・更新の補足

[READMEへ戻る](../README.md)

## 初期設定を先に行う

クローンしたディレクトリでCopilotを起動し、cdw-bootstrapのconfigureモードで調査・設定を行います。[初期設定規約](../.github/workflow/references/project-setup.md)に入力・可変領域・完了条件を定義しています。完了した.github/workflow/project/も導入時にコピーします。未設定の配布物だけでは案件開始できません。

## Notionに資料がある場合

[Notionセットアップ](../.github/workflow/references/notion-setup.md)に、接続コマンド・ログイン・コピペ用プロンプト・取得記録・接続できない場合の手順をまとめています。初期設定の前に実施してください。

## 導入されるもの

| 対象 | 動作 |
|---|---|
| `.github/agents/` | 担当別のmodel定義をコピー |
| `.github/skills/` | 14工程と7操作入口のスキルをコピー |
| `.github/workflow/` | 規約・ひな型・任意のレビュー定義をコピー |
| `.github/copilot-instructions.md` | 既存内容を保持し、専用ブロックを追記 |

Git履歴、テスト、`docs/creation/`の作成記録はコピーしません。異なる同名ファイルがあれば変更前に停止します。認証・親セッションのモデル・承認モードは自動変更しません。担当エージェントには配布定義のmodelを適用します。

## 開始前の確認

導入設定を対象プロジェクトの通常の運用でremote `develop`へ反映してください。作業ブランチは最新のremote `develop`から作るため、設定もその起点に必要です。反映後は作業ツリーをクリーンにします。ワークフロー自身はマージしません。

案件固有の技術スタック、コマンド、認証、リリース先は導入先のコードと環境を調べて決定します。配布物の検証例を案件の実行結果として転用しません。既存の要件定義の枠は後から取り込めます。

## スキルを認識しない場合

- Copilot CLI：利用可能なら`/skills reload`、`/skills list`で検出を確認します。
- VS Code：GitHub Copilotのエージェントモードを使用します。
- 自動検出が利用できない場合：対応する`SKILL.md`を明示的に読ませて実行します。これはネイティブスキル機能とは異なります。

利用可能な契約・認証・機能をbootstrapで確認します。利用できなければ停止し、別製品には自動で切り替えません。[公式仕様と対応状況](../.github/workflow/references/compatibility.md)を参照してください。

## 更新する場合

取得した更新内容を確認し、READMEと同じインストール手順を実行します。異なる既存ファイルは自動上書きしません。競合ファイルと`.github/copilot-instructions.md`の専用ブロックを比較し、手動で更新してください。

## 工程記録の保存

案件ごとに`/tmp/<repo-id>/<branch>/`へ保存します。例：`/tmp/orders-a1b2c3d4/feature.bulk-approval/`。

- 次の工程へ渡すのは、案件ルートの絶対パス・スキル名・モードだけです。本文や要約ではなく、指定ファイルを読み直します。
- 修正時は同じ工程MDを更新し、下部に履歴を追記します。
- `/tmp`消失に備え、導入時に永続的なチェックポイント先を決めます。
- WindowsではWSL等で`/tmp`の実在と権限を確認します。利用できなければ停止します。

詳細：[保存・受け渡し](../.github/workflow/references/artifacts.md)、[ブランチ準備](../.github/workflow/references/branching.md)、[PR添付](../.github/workflow/references/pr-artifacts.md)。

## コマンドの使い方

[操作コマンド一覧](commands.md)を参照してください。機械判定の設定は初期設定で具体化します。既存案件へ途中導入する場合、空の記録を合格扱いにせず、不足する承認・レビュー・証跡を揃えます。

## このリポジトリを検証する場合

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
```

[作成時の検証結果](creation/verification.md)と[リリース準備](creation/release-readiness.md)を参照できます。Copilot CLI・VS Code実機での動作はこの作成環境では未検証です。

スキルはCopilotへの実行手順です。導入だけで常駐処理や強制的なCIゲートにはなりません。Git権限・CI条件・デプロイ保護は導入先で設定します。

## v0.4.0からv0.4.1への名称変更

Copilot版の接頭辞は`gdw`から`cdw`へ変更しました。Gemini版は`gdw`を維持します。

既に旧Copilot版を導入している場合は、導入前に保存した旧版と照合し、今回の配布物が追加した旧`.github/skills/gdw-*`と任意の旧reviewer定義を特定してください。利用者が作成した同名ファイルは自動削除しません。旧版を退避して旧定義を除き、`.github/workflow/`と専用指示ブロックを新版と比較して更新した後、通常の導入を実行してください。案件の/tmp記録とチェックポイントはそのまま保持します。完了後にスキル一覧を再読込し、`cdw`だけが有効なことを確認します。

旧版のoptionalレビュアーを配置済みの場合は、新しい工程別review担当と競合しないよう旧定義を特定・退避してください。設定やモデルの権限は自動変更しません。モデル保守は[モデル割当規約](../.github/workflow/references/model-policy.md)に従います。

## v0.6.0への更新

[安全な更新手順](../.github/workflow/references/ops-update.md)を使用します。旧版導入は旧配布からadoptし、新版へupdateします。運用台帳とホスト観測のない旧案件は停止します。[初期化・移行](../.github/workflow/references/operations.md)に従って準備してください。
