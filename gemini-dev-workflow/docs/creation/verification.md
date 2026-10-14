# 作成時の検証結果

検証日：2026-10-13。環境：Linux、Python 3.12、Git 2.51.1、coverage.py 7.16.2。正確なコマンド・cwd・UTC日時・終了コード・ログハッシュはevidence/commands.json。

| 検証 | 結果 | 証拠 |
|---|---|---|
| UT | 19件成功 | evidence/unit-tests.log |
| install.py 行/分岐 | 56/56行、30/30分岐、100% | evidence/coverage.json |
| validate.py 行/分岐 | 35/35行、22/22分岐、100% | evidence/coverage.json |
| 結合テスト | UTと別実行、3件成功 | evidence/integration-tests.log |
| スキル形式・内部リンク・JSON | PASS、14スキル | evidence/static-validation.log |
| 独立再レビュー | 指摘4件解消・残存0 | review.md |
| 要件定義の初回応答シナリオ | 一問一答・枠の後日共有に対応 | scenarios.md |
| Git bundle/ZIP復元 | パッケージ作成時に別ディレクトリで検証 | ZIP内のPACKAGING-CHECKS.json |

## 検証範囲の限界

Gemini CLIはこの作成環境に存在せず、CLI実機の認証・スキル検出・ネイティブサブエージェント、VS Code拡張実機の確認は未実施。Windowsネイティブ実行も未実施。パス中の空白とCRLFはLinux上の実ファイルによるテストで確認したが、Windows実機合格と同一視しない。

本成果物は再利用可能な手順と導入ツールの配布物。導入先の業務コード・本番環境は提供されていないため、実案件の要件、工数、詳細設計、テスト結果、リリース承認を作り上げない。導入先bootstrapと各ゲートで実施する。実アプリの本番リリース準備完了や、Gemini実機での全工程合格は主張しない。

## v0.2.0 更新検証

2026-10-14：実装Pythonは変更なし。14スキル・参照資料・テンプレートを更新し、既存UT19件と結合3件、静的検証を再実行。結果とコマンドはevidence/に更新。別一時Gitリポジトリで、古いローカルdevelopを維持したまま最新remote developのfetch SHAからfeature.bulk-approvalを作成する手順に成功。evidence/branch-scenario-v0.2.0.json参照。Gemini実機で/tmpへのアクセス権限やPR添付機能は引き続き未検証。

## v0.2.2 導入手順の整理

READMEをclone→対象プロジェクトへ導入→Gemini開始へ変更。納品ZIPの展開とGit bundle復元の説明を通常導入から削除。PR添付ZIPとチェックポイントは維持。実装・スキル処理に変更なし。clone後の導入確認はevidence/clone-install-v0.2.2.jsonを参照。過去のバージョンの結果は履歴として保持。

## v0.2.3 READMEの可読性改善

READMEを12,494文字から2,109文字へ短縮。導入補足をdocs/setup.md、14スキルの固定入力・出力と共通規約の完全一覧をdocs/workflow-reference.mdへ整理。元の詳細一覧にある全ファイル名の維持と14工程の掲載を確認。静的検証はPASS。実装とスキルに変更はなく、UT・結合テストは再実行していない。

## v0.3.0 プロジェクト初期設定

クローン先で実行するconfigureモード、可変領域7ファイル、全source_rootsの読取台帳、初期設定の完了判定、各工程の固定入力を追加。独立手順レビューの2指摘（導入後の台帳再確定、全資料ルートの列挙）を反映。既存UT19件・結合3件は成功。可変領域7ファイルの導入、NOT_STARTED維持、再導入差分0件を確認。静的検証PASS。Gemini実機での初期設定実行は未検証。

## v0.3.1 Notionセットアップ

Notion公式MCPの接続・認証・依頼プロンプトを追加。configureから条件付きで参照し、URL・読了・保存先・原本更新を台帳管理する。静的検証PASS。Gemini/Notionの認証・実読取は未実施。実行コードの変更なし。

## v0.4.0 工程の機械検査と7項目の改善

| 検証 | 結果 |
|---|---|
| 導入・静的検査UT | 20件PASS |
| 工程ランタイム回帰 | 23件PASS。全14工程の正常経路と拒否経路 |
| 行・分岐カバレッジ | 544/544行、186/186分岐、100%。除外なし |
| 導入結合テスト | UTとは別実行、3件PASS |
| スキル・リンク・JSON | PASS |
| Gemini独自コマンドTOML | 7件PASS |
| 独立再レビュー | 確認範囲の重大な未解決指摘なし。quality-review.md参照 |

ランタイム453行/134分岐、install.py56行/30分岐、validate.py35行/22分岐。実行の原本はevidence/commands-v0.4.0.jsonと各ログ、coverage-v0.4.0.json。Gemini CLI実機での実行は未検証。

## v0.5.0 担当別モデル定義

51件PASS（UT20・工程回帰23・モデル契約5・導入結合3）。静的検査PASS。Python対象544行・186分岐のカバレッジ100%、除外なし。独立レビューの初回受付指摘は修正・再確認済み。実行原本は[evidence/commands-v0.5.0.json](evidence/commands-v0.5.0.json)、[coverage-v0.5.0.json](evidence/coverage-v0.5.0.json)。

実際のモデル起動、利用契約、個人設定との優先順位は実ホスト未検証。導入時にmodel-policy.mdの照合が必要。静的テストの合格をモデル実行の成功とは扱わない。

## v0.6.0 7項目の運用機能

| 検証 | 結果 |
|---|---|
| 既存UT | 20件PASS |
| 既存工程回帰 | 23件PASS |
| 運用機能 | 12件PASS。実Git fixture・更新競合/復元・資料改変/期限・hook拒否・評価記録・進捗失効 |
| モデル定義 | 5件PASS |
| 導入結合 | 3件PASS |
| 両版一致 | Copilot版で検査 |
| 合計 | 63件PASS |
| Python行・分岐 | 1077/1077行、312/312分岐、100%。除外なし |

実行原本：[commands-v0.6.0.json](evidence/commands-v0.6.0.json)、[coverage-v0.6.0.json](evidence/coverage-v0.6.0.json)。独立レビューはoperations-review.md。追加試験のホスト応答はモックであり、実AIによる試験合格ではない。

実ホストの認証・モデル選択・フック発火・Notion接続は未検証。導入先のdoctorとevaluateにより確認する。CLIを必要とし、IDE単独を同等検証済みと扱わない。
