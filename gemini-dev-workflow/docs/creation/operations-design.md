# 運用機能の設計 v0.6.0

配布先workflow/runtimeにops.pyとmaintenance.pyを追加。標準ライブラリのみ。ops.pyは既存gdw.py/cdw.pyをimportしてハッシュ・安全パス・承認・check/impact/advanceを再利用する。modelの正本は既存agentsのまま。

- doctor: 明示したhost-observations.jsonを検証。全担当のモデル/agent定義ハッシュ/ホスト版/上書き確認のホスト観測ログを照合。CLIバージョンはsubprocess argv、期限付き。読取証跡に本人性保証はない。
- quality: Git基準SHAと既定のtests/・CI・カバレッジ設定に追加のプロジェクト指定パスを統合して変更検出。削除も対象。承認は変更diffハッシュ・actor・理由・原文パス/ハッシュに紐付け。基準SHAはCIの保護設定から指定する。
- sources: MCP取得済み内容をローカル固定、URL/remote更新時刻/取得時刻/ハッシュを固定し、再取得結果と比較。リモート取得は既存Notion手順。期限切れ、観測欠落、一覧変更を拒否する。
- dashboard: gate/state/MD/実行記録を読みHTMLエスケープして静的HTML。見積/実績は明示構造JSON。未入力を0にしない。
- hooks: product別stdinを正規化。読取toolのみallow。write toolは範囲と承認確認。shellは承認済argvの完全一致（複合式は拒否）、未知tool拒否。レビューはread only。ケース未指定時は読取のみ許可。フックの自己改変耐性はOS/ホスト/CIで補う。
- eval: 保存先は新規ディレクトリのみ。Git developと小さなPython課題、対話シナリオを準備。明示--liveでのみホストを呼ぶ。ログ・モデル・exit・timeout・Git差分を記録し、独立評価のチェックリストと証跡が揃うまでPASSとしない。
- maintenance: install/adopt/update/restore。旧sourceから導入ベースを登録、管理領域だけ3者比較、ユーザー独自指示は保持。可変領域・個別modelも競合として可視化。全競合検査後のみ書込。バックアップ外部保存。復元も現在ハッシュ照合後実行。

案件のops.jsonは新規bootstrap時に初期化。doctor/sources/qualityの判定を既存check内部のoperation_guardで必須実行。ops gateは同じ必須判定の結果を進捗用に保存する。品質基準の変更を自動承認しない。古い案件の移行は明示初期化し未確認を保留。全工程は該当規約のみ読む。各機能のMDを同案件下に更新、操作履歴は追記。

## 確定時の補足

資料は実内容hashを承認に結合し、全行事前検証後に内容hash付き別名で固定する。失敗時は旧lock/gateを復元する。必須URLはprofileと照合する。更新はdry-run既定、全書込前に外部journalを保存し、失敗時復元する。配布版はsource READMEの版、実装版はmanager_versionで別記録。

実機試験はPREPARED/UNVERIFIED/FAIL/BLOCKED/PASSを区別。実行ログと対象ZIPを全シナリオ保存し、独立判定全合格だけPASS。進捗の失敗理由は保存し、PASSの期限はホスト/資料観測の最短期限。コードと案件証跡のhashも照合する。
