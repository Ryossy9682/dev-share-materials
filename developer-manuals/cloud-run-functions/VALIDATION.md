# 検証結果

確認日：2026-10-14

- Functions Framework 3.9.2を使い、5件のHTTP受入テストを実行して成功しました。空白・日本語・50/51文字の境界・GET・POSTを含みます。
- ローカルサーバーを実際に起動し、計測スクリプトから3回呼び出して、期待するJSONとCSV出力を確認しました。
- 上記実行環境はLinux / Python 3.12です。配布手順とクラウドのランタイム指定はPython 3.13です。
- Windows PowerShellのスクリプトは内容確認を行い、Windows PowerShell 5.1で日本語を扱えるUTF-8 BOM付きで保存しました。Windows上での実行は未検証です。
- Google Cloudへのデプロイ、IAM設定、クラウド側の課金・性能の実測は実施していません。

公式仕様の確認先： https://docs.cloud.google.com/run/docs/deploy-functions
