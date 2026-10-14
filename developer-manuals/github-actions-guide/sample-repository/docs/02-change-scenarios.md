# 初回・変更後・再実行の比較

データとSQLは架空の販売業務です。注文IDをキーとし、paidのみ売上に含め、割引後金額を売上と呼びます。返金や税の実業務ルールではありません。

| 変更 | phase1 | phase2 |
|---|---|---|
| 注文1 | 100、割引10%、paid | 110へ修正。更新時刻も変更 |
| 注文3 | pending | paidへ変更 |
| 注文4 | paid | cancelledへ変更 |
| 注文6 | paid | 元データから物理削除 |
| 顧客102 | standard | premiumへ変更 |
| 顧客104 | 存在 | 物理削除（注文には未登場） |
| イベントe4 | 未存在 | 新しいpaymentイベント |

初回にphase1でseed/build/Snapshotを実行してから、次でCSVだけを切り替えます。

```powershell
.\scripts\select-fixtures.ps1 -Project patterns -Phase phase2
.\.venv\Scripts\dbt.exe seed --project-dir projects/patterns --profiles-dir profiles --full-refresh
.\.venv\Scripts\dbt.exe build --project-dir projects/patterns --profiles-dir profiles `
  --exclude resource_type:seed --vars '{enable_patterns: true, enable_snapshots: true}'
```

この2回目のbuildには`--full-refresh`を付けません。差分更新と履歴を比較するためです。

| 対象 | phase1 | phase2の期待値・説明 |
|---|---|---|
| mart_sales_daily / p01_sales_view | 売上680、paid4件 | 売上349、paid3件 |
| p05_orders_merge | 売上680 | paid売上469。物理削除された注文6の120が残る |
| p06_orders_insert_overwrite | 売上680 | 指定3日を現在の全行で再構成し、paid売上349 |
| p04_events_incremental | 3イベント | 4イベント。同じ入力の再実行では新規対象0件 |
| snap_customers | 初回4顧客 | 102の旧行を閉じ、新行を追加。104は無効化。現在有効3顧客 |

MERGEの469は「売上として正しい」という期待値ではありません。更新だけの実装では物理削除を反映できないことを検出するための結果です。日次Martを正と比較し、削除フラグ、CDC削除イベント、定期再照合、対象範囲再作成等を設計します。

Snapshotは実行時点の変化を観測します。2回の実行の間に起きて消えた変更や、Snapshot開始前の過去履歴を自動復元しません。updated_atが更新されない変更もtimestamp戦略では検知できません。

7件のオフライン検算では、上記のほかlookbackより古い新規到着が取り込めないことと、10/3を完全に空にした追加ケースのパーティション削除を確認します。これはSELECTの検算と更新処理のシミュレーションであり、BigQueryのdbt生成DMLを実行した検証ではありません。

出典：

- https://docs.getdbt.com/docs/build/incremental-models
- https://docs.getdbt.com/reference/resource-configs/bigquery-configs
- https://docs.getdbt.com/docs/build/snapshots
