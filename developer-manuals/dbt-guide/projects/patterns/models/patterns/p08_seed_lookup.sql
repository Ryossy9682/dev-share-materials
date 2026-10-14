{{ config(materialized='view') }}
select o.order_id, o.status, labels.status_label
from {{ ref('stg_orders') }} as o
left join {{ ref('status_labels') }} as labels using (status)
