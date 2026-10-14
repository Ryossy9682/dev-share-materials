{{ config(materialized='incremental', incremental_strategy='merge', unique_key='order_id',
          on_schema_change='fail', partition_by={'field':'order_date','data_type':'date'}, cluster_by=['order_id']) }}
-- 再実行時は更新時刻に基づくlookback。物理削除は、このmergeだけでは伝播しません。
select order_id, customer_id, order_date, status, net_amount, updated_at
from {{ ref('stg_orders') }}
{% if is_incremental() %}
where updated_at >= timestamp_sub(
    coalesce((select max(updated_at) from {{ this }}), timestamp('1900-01-01')),
    interval {{ var('merge_lookback_days', 3) }} day
)
{% endif %}
