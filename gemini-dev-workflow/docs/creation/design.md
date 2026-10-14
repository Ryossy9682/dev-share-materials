# 配布物の詳細設計

要件版：1.0。既存の案件コードは本依頼の対象ではなく、再利用可能なワークフローを新規作成する。

| 対象 | 設計・契約 | 検証 |
|---|---|---|
| .gemini/skills/ | 14の工程。name/description、入力参照、手順、出力を各SKILL.mdに記載 | メタデータ・リンク検査、独立内容レビュー |
| references/ | 共通契約、工程、独立レビュー、変更範囲カバレッジ、見積もり、リリース、環境、出典に分割 | 要件追跡、分岐シナリオ |
| templates/ | 誤って合格と扱わない未確定・未実行の初期値 | JSON解析、内容レビュー |
| install.plan_install(target, source) | 既存targetを受け、(Path, bytes)の書込計画を返す。競合やリンクはValueError | 新規/既存/競合/同一/リンク/不正パス |
| install.main(argv) | argparse、既定dry-run。--applyだけ書込。設定・認証は変更しない | dry-run、実書込、再実行 |
| validate.validate(root) | スキル数・frontmatter・内部リンク・JSON・必須ファイルを確認しエラー一覧を返す | 正常/欠落/壊れたリンク/不正JSON/メタデータ |
| validate.main() | エラーがあれば終了コード1、なければ0 | 両終了コード |
| 任意reviewer定義 | read_file/grep_searchだけ。結果は親に返す。自動有効化しない | 構文・手順確認。Gemini実機は未検証 |

## 検証設計

UTは外部サービスなしの一時ディレクトリで実行し、実装ツール全行・分岐を計測する。結合は実際の配布物→別のGitプロジェクトへの導入→既存GEMINI.md保持→再導入→検証ツール実行の流れを別実行する。カバレッジはUTのみを採用する。ZIPのCRC、展開、Git bundleからの復元と履歴を確認する。独立レビューの担当はファイルを直接参照して指摘する。

今回の作成担当はGemini実機ではない。この作成記録の独立レビューを、納品したGeminiワークフローの実機レビュー成功と表現しない。

## v0.2.0 差分設計

新規実装コードなし。14スキルの固定入出力を明記し、保存先、ブランチ準備、PR添付の3規約を追加。初回requirements-setup→bootstrap→requirements本文の順にし、初回未作成と後続必須不足を区別。state.jsonをschema_version=2としbranch/repo_id/artifact_root/remote/取得日時を持たせる。同じMDに最新本文と追記履歴を保持する。

確認ケース：全リンクとJSON、既存導入22テスト、Git bare remoteのdevelop更新後にfetch SHAからfeature.xxxを作る動作、独立した文書レビュー。Plan Modeと/tmpの実機許可は導入先で確認し、許可を仮定しない。

## v0.3.0 初期設定設計

gdw-bootstrapにconfigureモードを追加。project-setup.mdを正本とし、project/の7ファイルへ再利用設定を保持する。GEMINI.mdとworkflowで未設定時の案件開始を防ぐ。工程正本は/tmp/<repo-id>/workflow-setup/。installerの既存再帰コピーを利用し、実行コードは変更しない。
