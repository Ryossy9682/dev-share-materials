# 移植の実装記録

| 要件 | 対応 |
|---|---|
| CP-01 | 14工程スキルと固定資料の参照を維持。マージ禁止・一問一答・要件照合・差し戻しを同じ本文で提供 |
| CP-02 | 60共通ファイルを元版から置換後に全文比較、runtimeは識別子置換後に全文一致。parity.jsonへ元/先SHAを保存 |
| CP-03 | .github/copilot-instructions.md、.github/skills/の21スキル。NotionのCopilot CLI/VS Code手順を整備 |
| CP-04 | 同じランタイム回帰23件、導入UT20件/IT3件、同等性2件。実機未検証をREADMEから辿れる資料へ明記 |
| CP-05 | feature.copilot-portへコミット。Copilot用READMEとソースZIPを作成 |

導入ツールはskills/workflowと指示ブロックだけを配置する。既存Copilot指示・認証設定・MCP設定・CIを保持し、同名ファイル競合は書込前に停止。Gemini版の作成証跡は改名流用せずCopilot版で再実行する。
