# dbt：基本構成・設計パターン・ベストプラクティス

`03-dbt-developer-guide.html`をブラウザーで開きます。図解、ケース比較、SQL/YAMLの例、運用・費用・品質の注意点を掲載しています。事例はすべて教材用の架空データです。

| フォルダー | 内容 |
|---|---|
| `projects/minimal/` | 小規模な日次売上Table。seedと1モデルから学習 |
| `projects/patterns/` | Staging、Ephemeral、Table、Incremental、Snapshot、テスト、契約、Exposure |
| `fixtures/phase1/` | 初回の注文・顧客・イベント |
| `fixtures/phase2/` | 金額修正、支払状態変更、キャンセル、注文の物理削除、顧客セグメント変更・削除 |
| `docs/cases/` | 12パターンの状況・メリット・デメリット・確認手順 |
| `scripts/` | セットアップ、CSV切替、7ケースのローカル検算 |
| `reference-only/` | source freshnessとBigQueryネイティブMVの参考例。既定のdbt実行対象外 |

教材の実行系はPython版dbt Core 1.10.13 / dbt-bigquery 1.10.3です。最新版の指定ではありません。現在のdbt v2やdbt platformの機能・提供範囲と、ここで検証したPython版のサンプルは区別します。バージョン更新時は互換性を確認してください。

最初に`docs/01-quickstart.md`をお読みください。クラウドを使わない検算は次の2コマンドです。

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\python.exe .\scripts\check_demo_offline.py
```

サンプルはクラウドへ自動実行されません。BigQuery上で実行する場合、事前に開発用プロジェクト・データセット・権限・課金を確認します。本番データセットへseedやfull-refreshを実行しないでください。

出典： https://docs.getdbt.com/docs/introduction
