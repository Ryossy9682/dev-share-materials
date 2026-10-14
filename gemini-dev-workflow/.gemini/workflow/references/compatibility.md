# 実行環境の適合確認

CLIとVS Codeで共通のGEMINI.md、工程手順、案件成果物を使用します。OS・シェル・Git・言語・依存管理・テストランナー・Gemini CLI版・IDE拡張版・契約区分を導入先で記録してください。秘密値は記録しません。

| 機能 | CLI | VS Code |
|---|---|---|
| GEMINI.md | プロジェクト指示として確認 | エージェントモードで読込を確認 |
| SKILL.md | 検出・有効化を実機確認 | 自動検出を仮定しない。なければ明示的なファイル読込 |
| 独立レビュー | カスタムサブエージェントまたは別セッション | 別セッション。利用可能なら独立エージェント |
| Plan Mode | 現行版の保存先・権限を確認 | 同名機能の存在を仮定せず、設計中は業務コードを変更しない |

CLIのPlan Modeでは/tmpへの文書保存やブランチ作成が許可されるとは限りません。必要な操作は通常の承認フローでモードを切り替え、ブランチ準備・工程MD保存の範囲だけ実行します。実行モードへの移行と業務要件の承認は別です。/tmpをPlan保存先として無断設定せず、保存できなければ停止します。正本は/tmp内に置き、次のスキルは正本を直接読みます。共有ディレクトリを読めない独立担当には正規の読取許可を確認するか、実ファイルを同一構造で移してハッシュを確認します。

Google公式のVS Code説明はCLIの全コマンド対応を保証していません。実際の機能一覧で確認し、利用不可は明示的読込または別Geminiセッションへ引き継ぎます。独立性を同一セッションの役割変更で代用しません。

2026-10-13時点：個人向けCLI/Code Assistの提供変更、Standard/Enterpriseの新規契約停止が告知されています。既存法人契約の利用可否は契約期間次第です。利用可能な正規認証・契約を確認し、不可ならBLOCKED。モデル名・契約・認証を勝手に選択せず、他製品へ自動移行しません。

出典： https://docs.cloud.google.com/gemini/docs/codeassist/use-agentic-chat-pair-programmer
https://geminicli.com/docs/cli/plan-mode/
https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals
https://docs.cloud.google.com/gemini/docs/codeassist/sunset

同名スキルが別階層や`.agents/skills/`にある場合は、実際に有効な定義のパスを確認します。別定義が優先される場合は黙って上書きせず競合を解消します。

## v0.6.0の実行要件

運用ゲートのdoctorがCLI版を実測するため、本製品のCLIをインストールした環境が必要。VS Codeは併用できるが、IDE単独を対応済みとしない。フックはCLI用の設定例を具体化し、実ホストで発火と拒否を確認する。
