# 配布物のカバレッジ対象

新規の実装コードはscripts/install.pyとscripts/validate.pyの全実行可能行・分岐。UT測定はcoverage.pyのbranch測定を有効化し、source=scriptsで未実行ファイルも対象にする。除外設定の追加は行わない。テストコードは実装カバレッジの分母に含めない。

Markdown、JSONテンプレート、Git bundleは実行可能コードではないため静的検査、独立レビュー、復元確認で検証する。任意のGeminiエージェント定義は構文・手順の確認までで、Gemini実機では未検証。

UTのみで計測し、結合テストは別実行する。生のcoverage JSONと実行ログをevidence/へ保存する。ソースハッシュをsource-hashes.jsonで固定する。
