-- 粒度：注文日ごとに1行。教材ではpaidのみを売上に含めます。
select
    order_date,
    count(*) as paid_order_count,
    sum(round(amount * (1 - discount_rate), 2)) as net_revenue
from {{ ref('raw_orders') }}
where lower(trim(status)) = 'paid'
group by order_date
