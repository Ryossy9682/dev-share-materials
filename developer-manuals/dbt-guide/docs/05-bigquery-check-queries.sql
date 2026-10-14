-- BigQueryコンソールへ貼り付ける確認用SQLです。
-- YOUR_PROJECT_IDを変更し、使用datasetが既定と異なる場合はdataset名も変更します。
-- 比較モデル・Snapshotを有効にしてbuildした後に使います。

-- 1) 全件Martと更新MERGE・範囲再作成の比較
select 'full_table_mart' as pattern, sum(net_revenue) as paid_total
from `YOUR_PROJECT_ID.dbt_demo_patterns.mart_sales_daily`
union all
select 'key_merge', sum(net_amount)
from `YOUR_PROJECT_ID.dbt_demo_patterns.p05_orders_merge`
where status = 'paid'
union all
select 'partition_overwrite', sum(net_amount)
from `YOUR_PROJECT_ID.dbt_demo_patterns.p06_orders_insert_overwrite`
where status = 'paid';
-- phase1: 680 / 680 / 680
-- phase2（full-refreshなし）: 349 / 469 / 349

-- 2) 物理削除された注文6がMERGEに残っていることの確認
select order_id, order_date, status, net_amount
from `YOUR_PROJECT_ID.dbt_demo_patterns.p05_orders_merge`
where order_id = 6;

-- 3) Snapshotの履歴と現在有効な行
select customer_id, segment, dbt_valid_from, dbt_valid_to
from `YOUR_PROJECT_ID.dbt_demo_patterns_snapshots.snap_customers`
order by customer_id, dbt_valid_from;

select count(*) as active_customer_count
from `YOUR_PROJECT_ID.dbt_demo_patterns_snapshots.snap_customers`
where dbt_valid_to is null;
-- phase1: 4 / phase2: 3
