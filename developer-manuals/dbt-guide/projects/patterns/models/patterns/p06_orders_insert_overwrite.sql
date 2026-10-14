{% set partitions_to_replace = [] %}
{% for date_value in var('rebuild_dates') %}
  {% do partitions_to_replace.append("date('" ~ date_value ~ "')") %}
{% endfor %}
{{ config(materialized='incremental', incremental_strategy='insert_overwrite',
          partition_by={'field':'order_date','data_type':'date'}, partitions=partitions_to_replace,
          on_schema_change='fail') }}
-- 対象日に属する現在の全行を取得します。変更行だけを返すSQLにしてはいけません。
select order_id, customer_id, order_date, status, net_amount, updated_at
from {{ ref('stg_orders') }}
{% if is_incremental() %}
where order_date in ({{ partitions_to_replace | join(', ') }})
{% endif %}
