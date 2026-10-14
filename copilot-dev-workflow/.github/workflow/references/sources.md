# 公式出典

確認日：2026-10-14（Asia/Tokyo）。導入時にも使用バージョンと対応を確認し、environment.mdへ記録します。

| 文書 | URL | 採用点 |
|---|---|---|
| Copilot Skills | https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills | .github/skills/・SKILL.md・明示呼出 |
| Custom instructions | https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions | .github/copilot-instructions.md・競合確認 |
| Custom agents | https://docs.github.com/en/copilot/reference/custom-agents-configuration | 任意レビュー定義・read/search |
| Copilot MCP | https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers | Notion HTTP接続 |
| VS Code MCP | https://code.visualstudio.com/docs/agents/reference/mcp-configuration | ユーザー設定・OAuth・実行環境差 |
| VS Code migration | https://code.visualstudio.com/docs/agent-customization/migrate-customizations | prompt filesに依存せずスキルを使用 |
| Notion MCP | https://developers.notion.com/guides/mcp/get-started-with-mcp | 公式エンドポイントと接続 |
| Git fetch | https://git-scm.com/docs/git-fetch | remote developの最新取得 |
| Git switch | https://git-scm.com/docs/git-switch | feature.xxx作成 |
| Coverage best practices | https://testing.googleblog.com/2020/08/code-coverage-best-practices.html | 数値以外のケース網羅・検出力確認 |

100%閾値、C/B/A見積もり、3回停止、マージ禁止、承認ゲート、工程MDとランタイムはユーザー指定の共通仕様です。製品の標準機能や公式の一律推奨とは区別します。

## 担当別モデル設定（v0.5.0確認）

https://docs.github.com/en/copilot/reference/custom-agents-configuration
https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference

## v0.6.0 運用機能の公式根拠

https://geminicli.com/docs/hooks/reference/
https://geminicli.com/docs/cli/headless/
https://docs.github.com/en/copilot/reference/hooks-reference
https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
