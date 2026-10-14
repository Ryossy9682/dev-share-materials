# 公式出典

確認日：2026-10-13（Asia/Tokyo）。以下はGoogle公式文書です。導入先ではインストール済みバージョンと文書の対応を再確認し、環境ファイルに確認日・URLを記録します。

| 文書 | URL | 採用点 |
|---|---|---|
| Agent Skills | https://geminicli.com/docs/cli/skills/ | ワークスペーススキル・必要時の読込 |
| Creating Agent Skills | https://geminicli.com/docs/cli/creating-skills/ | SKILL.md・name/description・リソース構成 |
| Skill best practices | https://geminicli.com/docs/cli/skills-best-practices/ | 明確な起動条件・段階的読込 |
| GEMINI.md | https://geminicli.com/docs/cli/gemini-md/ | プロジェクト共通指示 |
| Plan Mode | https://geminicli.com/docs/cli/plan-mode/ | 計画と実行の分離・書込制限 |
| Subagents | https://geminicli.com/docs/core/subagents/ | 独立コンテキスト・任意エージェント定義 |
| VS Code agent mode | https://docs.cloud.google.com/gemini/docs/codeassist/use-agentic-chat-pair-programmer | GEMINI.md・IDE機能差 |
| 個人向け提供変更 | https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals | 導入時の利用資格確認 |
| 法人向け提供変更 | https://docs.cloud.google.com/gemini/docs/codeassist/sunset | 契約状況の確認 |
| Coverage Best Practices | https://testing.googleblog.com/2020/08/code-coverage-best-practices.html | 数値だけで品質を判定しない |

100%の閾値、見積もりC/B/A、3回停止、マージ禁止、承認ゲート、案件成果物の形式はユーザー指定に基づく独自仕様です。Googleが100%を一律に推奨しているとは記載しません。公式コードのコピーではなく、この案件用の手順とテンプレートを作成しています。

2026-10-14追加確認：Git公式のfetch（https://git-scm.com/docs/git-fetch）とswitch（https://git-scm.com/docs/git-switch）、Gemini Plan Modeの保存制限。/tmp構成・固定ファイル読込・feature.xxx命名・同一MD更新はユーザー指定の独自仕様。

2026-10-14追加確認（v0.4.0）：

| 文書 | URL | 採用点 |
|---|---|---|
| Custom commands | https://geminicli.com/docs/cli/custom-commands/ | プロジェクトのTOML・名前空間・引数 |
| Hooks | https://geminicli.com/docs/hooks/ | フックだけに判定を依存させない |
| Hooks best practices | https://geminicli.com/docs/hooks/best-practices/ | 実行失敗・入力検証・信頼境界 |
| Policy engine | https://geminicli.com/docs/reference/policy-engine/ | 設定権限を勝手に変更しない |

機械ゲート・復旧ランタイム・要件対応検査・変異テストは本リポジトリ独自の実装です。

## 担当別モデル設定（v0.5.0確認）

https://geminicli.com/docs/core/subagents/
https://geminicli.com/docs/cli/model/
https://geminicli.com/docs/get-started/gemini-3/

## v0.6.0 運用機能の公式根拠

https://geminicli.com/docs/hooks/reference/
https://geminicli.com/docs/cli/headless/
https://docs.github.com/en/copilot/reference/hooks-reference
https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
