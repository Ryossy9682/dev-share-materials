{{ config(materialized='table', partition_by={'field':'order_date','data_type':'date'}, cluster_by=['customer_id']) }}
-- Looker Studio向けに必要な列だけ用意する、注文粒度の横持ちTableです。
select order_id, order_date, customer_id, segment, status_label, net_amount
from {{ ref('p03_orders_enriched_table') }}
where status = 'paid'
