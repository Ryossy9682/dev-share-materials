# セットアップと最初の実行

PowerShell、Python 3.12、Google Cloud CLIを前提にしています。dbt CLIはBigQueryへSQLを送るツールであり、以下にはBigQueryのbq CLIは使いません。

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\dbt.exe --version
$env:DBT_PROJECT = "YOUR_PROJECT_ID"
$env:DBT_LOCATION = "asia-northeast1"
gcloud auth application-default login
```

BigQueryコンソールで開発用データセット`dbt_demo_minimal`と`dbt_demo_patterns`を用意します。Snapshotも試す場合は、既定のschema生成に対応する`dbt_demo_patterns_snapshots`も同じロケーションに用意します。DBT_DATASETを変更した場合は、その名前に`_snapshots`を付けたdatasetが既定のSnapshot保存先です。接続先とソースのロケーションをそろえます。読み取り対象にはData Viewer相当、書込先にはData Editor相当、ジョブ実行プロジェクトにはJob User相当の権限を担当者と確認します。データセット自動作成を使うなら作成権限も必要です。

`profiles/profiles.yml`はセットアップ時にexampleから作成します。methodはoauthで、ローカルADCを使用します。DBT_DATASETを設定すると両プロファイルの出力先を上書きするため、同名モデルを同じデータセットへ作らないようにします。

最小プロジェクトの実行：

```powershell
.\.venv\Scripts\dbt.exe debug --project-dir projects/minimal --profiles-dir profiles
.\.venv\Scripts\dbt.exe seed --project-dir projects/minimal --profiles-dir profiles --full-refresh
.\.venv\Scripts\dbt.exe build --project-dir projects/minimal --profiles-dir profiles --exclude resource_type:seed
```

期待値は3日分の売上合計680、入金済み注文4件です。金額は教材用で、税・通貨変換・返金会計を含みません。

パターン比較プロジェクトの基本構成：

```powershell
.\.venv\Scripts\dbt.exe seed --project-dir projects/patterns --profiles-dir profiles --full-refresh
.\.venv\Scripts\dbt.exe build --project-dir projects/patterns --profiles-dir profiles --exclude resource_type:seed
```

基本構成では13モデル中の比較用8モデルとSnapshotを無効にしており、Staging3・Ephemeral1・Mart1を使います。比較モデル・Snapshotを有効にするには、最初のphase1で次を実行します。

```powershell
.\.venv\Scripts\dbt.exe build --project-dir projects/patterns --profiles-dir profiles `
  --exclude resource_type:seed --vars '{enable_patterns: true, enable_snapshots: true}'
```

sourceは外部テーブルの定義なので、source()とseedの間に自動の作成依存はありません。そのため、この教材ではseedを先に実行します。実務では元データの取り込みを別の仕組みで行い、sourceで参照します。

資料生成・テスト：

```powershell
.\.venv\Scripts\dbt.exe test --project-dir projects/patterns --profiles-dir profiles --select test_type:unit
.\.venv\Scripts\dbt.exe docs generate --project-dir projects/patterns --profiles-dir profiles
.\.venv\Scripts\dbt.exe docs serve --project-dir projects/patterns --port 8080
```

parseはプロジェクト解析です。compileやdocs generateはアダプターの処理・メタデータ参照等で接続が必要になる場合があります。テストもBigQuery上のクエリとして費用が発生し得ます。

出典：

- https://docs.getdbt.com/reference/commands/build
- https://docs.getdbt.com/docs/build/sources
- https://docs.getdbt.com/docs/build/seeds
- https://docs.getdbt.com/docs/build/unit-tests
