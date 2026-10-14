# プロジェクト初期設定

これは案件開発より前の工程。gdw-bootstrapのconfigureモードで実行する。案件のbranch.md、requirements.md、state.jsonは要求しない。featureブランチ作成・業務実装・本番操作・マージは行わない。

## 入力と可変領域

最初にGEMINI.md、gdw-bootstrap/SKILL.md、この規約、`.gemini/workflow/project/profile.json`を読む。既存の可変領域7ファイルも読む。これらのパスは作業中のワークフロールート基準。

1. クローンした現在のディレクトリをworkspace_rootとして確認する。対象コードと資料がその配下にあれば調査する。ワークフロー配布物だけで開発対象がなければ、対象プロジェクトの場所または資料の配置先を質問する。配布物のPythonや作成記録を開発対象の技術・仕様に転用しない。
2. 調査するsource_rootsとtarget_rootを絶対パスで記録する。外部ディレクトリがGeminiから読めない場合は利用者にアクセス設定または資料の配置を依頼する。アクセス制限を迂回しない。
NotionのURLが提供された場合は[Notionセットアップ](notion-setup.md)を読み、notion_sourcesへ登録して、ローカル資料と併せて全対象ページを順次取得する。案件開始時の原本照合にもNotionのページと子ページ一覧を含める。

3. クローン元workspace_rootを必ず含む全source_rootsを再帰列挙し、全ディレクトリの構成、コード、README、要件枠、設計資料、アーキテクチャ概念資料、テンプレート、CI、依存定義、テスト・リリース設定をinventory.mdへ列挙する。無視設定で見えていない資料も確認する。秘密値、.git内部、依存物、キャッシュ、生成物は内容を読み込まず、除外範囲と理由を記録する。シンボリックリンクは無断で対象範囲を広げない。
台帳の変更検出対象から、この処理が生成するproject/、/tmpの工程記録、チェックポイントを除外し、自己更新でSTALEを繰り返さない。ワークフロー共通定義の変更は別途その版で管理する。

4. 台帳の対象ファイルをすべて順次読む。一括プロンプトへの詰め込みではなく、区切って読み、読了状態と原本ハッシュを記録する。PDF・画像・表計算なども対応する読取手段で確認する。未対応形式・権限不足・途中までの読取を完読扱いにしない。対象資料の未読があればBLOCKED。
5. structure.mdへ構成と依存関係、architecture.mdへ境界・データフロー・設計規約、templates.mdへ工程別に採用する原本と使い方、commands.mdへ実際のコマンド・cwd・環境・証跡を記録する。必要な原本は許可された永続場所に保持し、導入後のパスから読めることを確認する。汎用テンプレートを補う場合も必須の証跡・承認項目を落とさない。
6. 不足情報・矛盾・実行不能をprofile.jsonのunresolvedへ記録し、必要な質問で解消する。適用しない項目は理由を明記する。危険なコマンドを検証目的で実行しない。本番系コマンドは構成照合までとし、実行未検証を明記する。

## 記録と終了条件

工程記録の正本は`/tmp/<repo-id>/workflow-setup/`の同名MDとprofile.json。同じファイルを更新し履歴を追記する。初回は可変領域から初期化し、再開時はprofile.jsonのsetup_artifact_rootから正本を読む。確定した設定を`.gemini/workflow/project/`へ反映して以後の固定入力にする。これは再利用設定であり案件工程MDとは区別する。永続チェックポイントを設定し、/tmp消失時はそこから復元する。正本もチェックポイントもなければ再調査する。

review.mdで、対象資料の読了、全出典の到達可能性、構成・設計・テンプレートの整合性、コマンドと実行環境、未解決事項0件を照合する。未入力・架空値はFAIL。完了時だけprofile.json.statusをREADYにし、原本版・台帳ハッシュ・対象ルートを記録する。「初期設定完了」と調査対象・残る実機検証範囲を示して終了する。案件開発は別の依頼で開始する。

## 案件開始後の固定入力

全スキルがprofile.jsonを読み、READY・対象ルート一致を確認する。workflowは開始時に原本の追加・削除・変更を台帳と照合し、変化があればSTALEにしてconfigureへ戻す。bootstrapは案件のenvironment.mdへ採用設定の版とパスを記録し、その環境で再確認する。

| スキル | profile.jsonに加えて読む可変領域のファイル |
|---|---|
| gdw-workflow | inventory.md, review.md |
| gdw-bootstrap | inventory.md, structure.md, architecture.md, templates.md, commands.md, review.md |
| gdw-requirements | templates.md, architecture.md |
| gdw-investigate | inventory.md, structure.md, architecture.md |
| gdw-estimate | structure.md, commands.md |
| gdw-design | structure.md, architecture.md, templates.md, commands.md |
| gdw-review-design | structure.md, architecture.md, templates.md, commands.md |
| gdw-implement | structure.md, architecture.md, commands.md |
| gdw-review-implementation | structure.md, architecture.md, commands.md |
| gdw-tests | structure.md, architecture.md, templates.md, commands.md |
| gdw-review-tests | structure.md, architecture.md, templates.md, commands.md |
| gdw-verify | architecture.md, commands.md |
| gdw-deliver | templates.md, commands.md |
| gdw-release | architecture.md, commands.md |

別ディレクトリへ導入した場合は、導入先でconfigureを再実行し、workspace_root・target_root・原本パスの到達可能性を照合する。導入で変更されたGEMINI.md・共通定義も差分を読み、導入後の原本ハッシュと台帳を確定し直してからREADYとする。単なる絶対パス置換でREADYを引き継がない。共有設定には各端末で解決できるルート基準の相対参照を優先し、端末固有パスは導入時に再解決する。

各工程は表のファイルが指す対象原本も必要に応じて直接読む。独立レビューの案件基準requirements.md等は引き続き必須。可変領域から共通のマージ禁止・承認・品質基準は緩和できない。

## 機械検査の準備

commands.mdへランタイムを動かすPython、UT・結合・計測レポートの形式、独立レビューIDの採番方法、永続チェックポイント先、CIの実行場所を確定する。Notion取得内容を含む原本と工程の依存関係を調査する。詳細は[runtime.md](runtime.md)。

初期設定の最終確認はmodel-policy.mdに従い、check担当のconfigure-reviewモードへ委任する。軽量の設定担当だけでREADYを確定しない。

## 運用機能の導入

[運用機能の入口](operations.md)に従い、ホスト観測・担当別フック・導入基準登録・実ホスト試験を設定する。実機試験をまだ実行できない場合はその状態をreview.mdに明示し、実機検証済みとして扱わない。
