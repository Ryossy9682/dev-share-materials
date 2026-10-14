# 操作コマンド

[READMEへ戻る](../README.md)

Gemini CLIで利用します。追加後に見つからなければ`/commands reload`、`/commands list`で確認してください。VS CodeのGemini Code Assistが同じ独自コマンドを持つとは仮定せず、統合ターミナルのGemini CLIを使うか対応するスキルを明示して読みます。

| 操作 | 入力例 | 結果 |
|---|---|---|
| 初期設定 | `/gdw:setup` | コード・Notion・テンプレートを調査し可変領域を完成 |
| 案件開始 | `/gdw:start` | ブランチ準備と一問一答の要件定義 |
| 状況確認 | `/gdw:status /tmp/repo-id/feature.xxx` | 現在工程・停止理由・次の操作 |
| 再開 | `/gdw:resume /tmp/repo-id/feature.xxx` | 証跡を確認して再開。消失時はチェックポイントから復元 |
| 工程検査 | `/gdw:check /tmp/repo-id/feature.xxx` | 必須資料・承認・レビュー・テストの整合性を検査 |
| 変更影響 | `/gdw:impact /tmp/repo-id/feature.xxx` | 資料変更と再確認する工程を表示 |
| 検出力確認 | `/gdw:mutate /tmp/repo-id/feature.xxx` | レビュー済みの欠陥注入計画を使い捨てコピーで実行 |

コマンドは各手順への入口です。引数には案件ルート等だけを渡し、前工程の本文をコピーしません。初期設定不足や実行権限不足は停止理由として表示します。

## スクリプトを直接実行する場合

Python実行名は導入環境に合わせてください。以下のパス・ブランチは例です。

```sh
python .gemini/workflow/runtime/gdw.py --case /tmp/repo-id/feature.xxx init --repo /absolute/project --branch feature.xxx --checkpoint-dir /absolute/checkpoints
python .gemini/workflow/runtime/gdw.py --case /tmp/repo-id/feature.xxx status
python .gemini/workflow/runtime/gdw.py --case /tmp/repo-id/feature.xxx record
python .gemini/workflow/runtime/gdw.py --case /tmp/repo-id/feature.xxx check
python .gemini/workflow/runtime/gdw.py --case /tmp/repo-id/feature.xxx advance
```

`init`は案件初回準備後に1回だけ行います。`record`は現在の成果物と入力を記録するだけで、合格や人の承認を与えません。`advance`は機械検査と永続チェックポイント保存に成功してから進行します。失敗を無視して続行する運用はしません。

```sh
python .gemini/workflow/runtime/gdw.py --case /tmp/repo-id/feature.xxx impact
python .gemini/workflow/runtime/gdw.py --case /tmp/repo-id/feature.xxx checkpoint /absolute/checkpoints/manual.zip
python .gemini/workflow/runtime/gdw.py --case /tmp/repo-id/feature.xxx restore /absolute/checkpoints/manual.zip
```

`restore`は空の案件ルート専用です。コード・ブランチ・Notionの原本は復元しません。詳細は[機械検査・復旧規約](../.gemini/workflow/references/runtime.md)を参照してください。

公式：[Gemini CLI独自コマンド](https://geminicli.com/docs/cli/custom-commands/)
