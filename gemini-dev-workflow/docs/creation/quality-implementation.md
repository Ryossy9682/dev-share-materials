# v0.4.0 実装と要件対応

| 要件 | 実装 | 検証 |
|---|---|---|
| DX-01 | runtime/gdw.pyのcheck/advance、全14スキルの固定規約 | 不足・古い証跡・未承認・不正履歴の拒否、14工程正常系 |
| DX-02 | .gemini/commands/gdw/の7コマンド、install.py | TOML解析7件、導入先へのコピーと再導入 |
| DX-03 | trace、coverage、review | REQ/AC不足・参照ハッシュ・UT/IT分離・行/分岐不足 |
| DX-04 | checkpoint/restore | manifest、改変・パス逸脱・symlink・上書き拒否、保存失敗 |
| DX-05 | impact、source_map、Notion snapshot | 追加/削除/変更、対象外文書、共有MD更新、後続無効化 |
| DX-06 | mutate、mutations | killed/survived/invalid、timeout、構文エラー、計画改訂後の旧証拠拒否 |
| DX-07 | tests/test_runtime.py、CI | ランタイム23件、既存/導入UT20件、結合3件 |

実装の具体的パスは`.gemini/workflow/runtime/gdw.py`。機械判定の固定入力・出力はruntime.md、JSONの項目例はtemplates/gate.jsonに記載。カバレッジ入力はcoverage.py互換JSONとし、他言語の計測変換は導入時に設定・検証する。

導入ツールはskills/workflow/commandsだけをコピーし、Pythonキャッシュと利用者のsettings.jsonを配布しない。
