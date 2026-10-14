{{ config(materialized='view') }}
select order_date, count(*) as paid_order_count, sum(net_amount) as net_revenue
from {{ ref('int_paid_orders_ephemeral') }}
group by order_date
