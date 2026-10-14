# 7項目の実装

runtime/ops.py: doctor、資料固定/再固定、品質差分承認、既存ゲートへの接続、フック入出力、進捗HTML。
runtime/maintenance.py: 導入/adopt/3者更新/外部journal/復元。既定dry-run、競合時無変更、個別設定保持。
runtime/evaluate.py: 使い捨てGit fixture、5段階の実ホスト試験、実行記録/コードと案件ZIP、独立判定。

14工程のSKILLからoperations.mdへ接続。詳細規約7枚と各入力JSONテンプレート、ホスト別フック設定、CI採用例を配布。新しいモデル正本は追加せず、既存agentsのmodelを使用する。Copilotはネイティブの設定/入力/出力を使用し、共通処理は明示置換後の一致検査で管理する。

プロジェクト初期設定は可変領域のまま。ホスト観測・Notion取得・人の承認・利用可能モデルを生成で埋めない。旧案件は運用証跡が揃うまでBLOCKED。独立レビューの3担当は読取専用、check等の機械検査担当は検証済argvのみ実行する。
