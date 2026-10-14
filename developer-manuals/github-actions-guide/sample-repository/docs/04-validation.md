# 検証実績

確認日：2026-10-14。Linux / Python 3.12 / dbt Core 1.10.13 / dbt-bigquery 1.10.3。

- 最小プロジェクトの`dbt parse`が成功しました。
- パターン比較プロジェクトの基本設定と、比較モデル・Snapshotを有効にした設定の`dbt parse`が成功しました。
- 有効化時のmanifestでは、13モデル、4seed、1Snapshot、3Source、23Data test、1Unit test、1Analysisを確認しました。
- DuckDB 1.3.2とSQLGlot 26.16.4でSELECTを検算する7ケースが成功しました。金額・粒度・seed結合・再実行・更新・物理削除・lookback範囲外・空パーティションの事例を含みます。
- オフライン検算では、BigQuery SQLのSELECTをDuckDB向けに変換し、Ephemeral等も検算用の一時的なTableとして評価します。BigQueryにおけるView/Table/IncrementalのDDL/DML、費用、同時実行、Snapshotの実動作を検証したものではありません。
- BigQueryでのdbt seed/build/test/snapshot/Source freshness、クラウドの接続・IAM・課金、Windows PowerShell上の実行は未検証です。

実環境では、開発用datasetで初回、phase2、同じ入力の再実行、遅延・削除・スキーマ変更・full-refreshを確認してから採用してください。parseの成功は、クラウドのSQL実行や権限の成功を保証しません。

出典： https://docs.getdbt.com/reference/commands/parse
