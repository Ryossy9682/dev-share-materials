{{ config(partition_by={'field': 'order_date', 'data_type': 'date'}, contract={'enforced': true}) }}
-- 粒度：order_dateごとに1行。基準となる全件再作成のモデルです。
select
    order_date,
    count(*) as paid_order_count,
    sum(net_amount) as net_revenue
from {{ ref('int_paid_orders_ephemeral') }}
group by order_date
