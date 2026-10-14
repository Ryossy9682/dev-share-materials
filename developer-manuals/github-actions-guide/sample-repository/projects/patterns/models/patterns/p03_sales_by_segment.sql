{{ config(materialized='table') }}
select segment, count(*) as paid_order_count, sum(net_amount) as net_revenue
from {{ ref('p03_orders_enriched_table') }}
where status = 'paid'
group by segment
