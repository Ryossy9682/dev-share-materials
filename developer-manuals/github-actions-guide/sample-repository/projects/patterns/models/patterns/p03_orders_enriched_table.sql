{{ config(materialized='table', partition_by={'field':'order_date','data_type':'date'}, cluster_by=['customer_id']) }}
-- 複数Martで使う共通の結合結果を保存する例です。
select o.order_id, o.customer_id, o.order_date, o.status, o.net_amount,
       c.segment, labels.status_label
from {{ ref('stg_orders') }} as o
left join {{ ref('stg_customers') }} as c using (customer_id)
left join {{ ref('status_labels') }} as labels using (status)
