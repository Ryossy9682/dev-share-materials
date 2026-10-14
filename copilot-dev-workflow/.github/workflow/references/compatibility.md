# 実行環境の適合確認

対象はCopilot CLI、またはVS CodeのCopilotエージェント機能です。OS・シェル・Git・言語・依存管理・テストランナー・Copilot版・IDE版・契約区分をenvironment.mdへ記録します。認証の秘密値は記録しません。

| 項目 | 確認すること |
|---|---|
| 共通指示 | .github/copilot-instructions.mdが実際に読み込まれる |
| スキル | .github/skills/の14工程と7操作。CLIは/skills list、/skills infoで確認 |
| 独立レビュー | 作成者とは異なるセッション、または独立コンテキスト。役割名の切替だけでは代用しない |
| Plan/実行権限 | /tmp保存とブランチ作成の可否。必要な操作範囲だけ正規の承認フローで許可する |
| 外部資料 | Notion認証、指定コードと全資料、保存済み原本への到達性 |
| 保存先 | /tmpの書込と永続チェックポイント。WindowsはWSL等で実在を確認 |

VS Codeはバージョンとエージェント実行方式により対応が異なります。この配布物はprompt filesへ依存せず、Agent Skillsを使用します。検出されなければ対応するSKILL.mdを明示して読みます。標準機能で案件ディレクトリを読めない場合は、承認されたワークスペース追加・アクセス設定かCopilot CLIを使用し、制限を迂回しません。本文の要約で代用しません。

クラウドエージェントは別の実行環境です。ローカル/tmp・Notion認証・作業ツリーが共有されるとは扱いません。クラウドへ移す場合は検証済みチェックポイント・コード・必要な認証を正規手順で用意し、環境照合が完了するまでBLOCKEDです。

既存GEMINI.md、AGENTS.md、他階層の同名スキルがある場合は有効な指示と競合を確認します。自動で優先順位を決めて規約を緩和しません。通常はGemini版と別ディレクトリで利用します。契約・モデル・承認設定は利用者の設定を維持します。

公式：
- https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills
- https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions
- https://code.visualstudio.com/docs/agent-customization/migrate-customizations

## v0.6.0の実行要件

運用ゲートのdoctorがCLI版を実測するため、本製品のCLIをインストールした環境が必要。VS Codeは併用できるが、IDE単独を対応済みとしない。フックはCLI用の設定例を具体化し、実ホストで発火と拒否を確認する。
