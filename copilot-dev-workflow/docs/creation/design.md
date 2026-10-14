# 移植設計

正本はGemini版e43c762。Copilot配布版は同正本から生成し、共通部分をハッシュで照合する。

| Gemini | Copilot |
|---|---|
| GEMINI.md | .github/copilot-instructions.md |
| .gemini/skills/ | .github/skills/（同じ14工程） |
| .gemini/workflow/ | .github/workflow/ |
| .gemini/commands/gdw/*.toml | .github/skills/cdw-<操作>/SKILL.md（7入口） |

runtimeは無変更。installerは配置先のみ変更し、既存指示保持・競合停止を維持。21スキルを静的検証。Notion/互換性/任意レビュー定義はホスト固有仕様として移植。クラウドエージェントをローカル/tmpの継続利用先とはみなさない。

2026-10-14更新：Copilot側の識別子・ランタイム名・一時ファイル接頭辞をcdwへ統一。元版との比較はgdw→cdwの明示置換を追加。
