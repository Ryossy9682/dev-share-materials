# モデル割当と実行規約

全工程の固定入力。モデル定義の正本は各エージェントファイルの`model`欄。SKILL.mdを読んだだけではモデルは切り替わらない。

## 実行担当の選択

1. 操作・工程に対応するagents内の定義を読み、必要なモデルを確認する。Autoやinheritで代用しない。
2. 対応する名前のカスタムエージェントを実際に起動する。既にその担当・指定モデルで実行中なら、そのまま対応SKILL.mdの処理を行い、自分自身を再起動しない。
3. 定義、ホストの有効設定・モデル表示・起動結果を照合する。上書き・フォールバック・利用不可・実モデル不明はBLOCKED。自己申告だけで確認済みにしない。
4. サブエージェントを利用できなければ、指定モデルを明示した別セッションで実行する。同一モデルのまま手順だけ切り替えて代用しない。対応できない環境では停止する。
5. 担当へ渡すのはスキル名・案件ルート絶対パス・モードのみ。工程の本文や要約を渡さない。初期設定だけは対象ルート、新規案件のブランチ確定前だけは下記の受付ルートを使う。担当自身が指示ファイル・規約・固定入力を直接読む。

## 新規案件の受付

最初の委任より前に、親は`/tmp/<repo-id>/workflow-intake/request.md`へ利用者の依頼原文・対象Gitルート・受付日時を保存する。既存の未完了受付は上書きせず、同じ案件の再開か確認する。受付ルートの絶対パスとモード`requirements-setup`を渡し、start/workflow/requirements担当はその直下のrequest.mdを固定入力として読む。未作成なら停止する。ブランチ未確定時は案件台帳・gate.jsonを要求しない。

要件担当が一問ずつ作る質問と利用者の回答は、ブランチ確定までは親がrequest.mdへ原文で追記する。ブランチ作成後、親は原文と履歴を案件ルートのrequirements.mdへ転記し、受付ファイルに移行先を記録する。要件担当は両ファイルの転記一致を確認する。以降は案件ルートを渡し、requirements.mdを正本とする。受付ファイルは監査用に保持する。別案件を始める際は完了受付を日時付きで退避してから新規作成する。依頼本文を委任メッセージで代用しない。

統括担当は配車・記録・人への伝達を行う。子担当は別工程へ進まず、指定工程の結果・次工程の識別子・不足事項を返して終了する。次の担当は親が起動する。ネスト委任を必須にしない。要件担当内のbootstrap・investigate・estimateへの移動も親へ返す。異なるモデルが必要な工程を同じ担当が続行しない。

要件定義の質問は高性能担当が一問だけ作る。直接質問できなければ親が原文のまま提示して待ち、利用者の回答をrequirements.mdへ原文で保存する（ブランチ確定前はrequest.md）。再実行する担当は同ファイルを読む。回答や人の承認を推測しない。

独立レビューは作成者と異なるセッション/独立コンテキストに限定する。レビュー担当は読み取り専用。親は原文を所定レビューMDへ保存し、評価を変更しない。モデルが違うだけで独立レビュー完了とは扱わない。

## チェック工程の境界

初期設定の最終確認はcheck担当のconfigure-reviewモードで行う。project/profile.json、inventory.md、structure.md、architecture.md、templates.md、commands.md、review.mdと実原本を読み、project-setup.mdの完了条件を確認する。案件ルートやgate.jsonはまだ要求しない。親が結果をsetupのreview.mdへ記録し、未解決ならREADYにしない。

通常のcheckはruntime checkを実行して判定する。差分影響と変異テストの評価も高性能担当へ割り当てる。テストコード作成・実行は軽量担当、網羅性と要件充足の独立判定はreview-tests担当。リリース実行は軽量担当で行うが、事前ゲートはcheck担当、反映後の動作確認はverify担当へ戻す。人の本番承認とマージ禁止を維持する。

## 記録と保守

各工程MDの実行記録へ、担当名・モデル定義のパスとハッシュ・要求モデル・観測した実モデル・ホスト版・セッションID・確認日時・確認根拠のログ/画面の参照を残す。失敗や切替履歴も同じMDへ追記する。認証値は記録しない。

モデル変更時は対象agentsファイルのmodelを更新し、利用可能モデル一覧、同じクラス（高性能/軽量）である根拠、検査、実機の小さな試行を確認する。階層・個人設定で別の同名定義が有効になっていないかも調べる。変更後にエージェントを再読込/再起動し、実モデルを照合する。前のモデル名へ戻せるようGit履歴と運用記録を保持する。

下記一覧は初期値の案内。実行時は各ファイルのmodelが正本。静的テストは欄の欠落・Auto/inherit・クラス違反・参照切れを検出するが、ホストが指定モデルを実際に使用したことは実機で確認する。利用不可でも別クラスへ自動降格しない。

## Gemini CLI固有の確認

.gemini/agents/<担当名>.mdを使用する。/agentsで定義を確認し、@担当名による委任またはネイティブの対応ツールで起動する。/modelは親のモデル選択であり、子の固定modelを書き換える操作ではない。settings.jsonのagents.overridesやmodelConfigsによる上書きも照合する。Gemini Code Assistが同じ定義を実行できるとは仮定せず、未対応時はGemini CLIの別セッションで同じmodelを明示して実行する。

初期値：高性能=gemini-3.1-pro-preview、軽量=gemini-3-flash-preview。Gemini CLI公式で確認できた明示IDを採用。導入時に提供終了・契約可否を確認し、利用不可なら同クラスの正式IDへ更新する。Haiku/LunaはGemini CLIの初期値には指定しない。

公式：https://geminicli.com/docs/core/subagents/ 、https://geminicli.com/docs/cli/model/ 、https://geminicli.com/docs/get-started/gemini-3/

## 全担当の割当

| 担当 | クラス | 初期モデル | 定義ファイル |
|---|---|---|---|
| workflow | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-workflow.md` |
| bootstrap | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-bootstrap.md` |
| requirements | 高性能 | `gemini-3.1-pro-preview` | `.gemini/agents/gdw-requirements.md` |
| investigate | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-investigate.md` |
| estimate | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-estimate.md` |
| design | 高性能 | `gemini-3.1-pro-preview` | `.gemini/agents/gdw-design.md` |
| review-design | 高性能 | `gemini-3.1-pro-preview` | `.gemini/agents/gdw-review-design.md` |
| implement | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-implement.md` |
| review-implementation | 高性能 | `gemini-3.1-pro-preview` | `.gemini/agents/gdw-review-implementation.md` |
| tests | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-tests.md` |
| review-tests | 高性能 | `gemini-3.1-pro-preview` | `.gemini/agents/gdw-review-tests.md` |
| verify | 高性能 | `gemini-3.1-pro-preview` | `.gemini/agents/gdw-verify.md` |
| deliver | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-deliver.md` |
| release | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-release.md` |
| setup | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-setup.md` |
| start | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-start.md` |
| status | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-status.md` |
| resume | 軽量 | `gemini-3-flash-preview` | `.gemini/agents/gdw-resume.md` |
| check | 高性能 | `gemini-3.1-pro-preview` | `.gemini/agents/gdw-check.md` |
| impact | 高性能 | `gemini-3.1-pro-preview` | `.gemini/agents/gdw-impact.md` |
| mutate | 高性能 | `gemini-3.1-pro-preview` | `.gemini/agents/gdw-mutate.md` |
