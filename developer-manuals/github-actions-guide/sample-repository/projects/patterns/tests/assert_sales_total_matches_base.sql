with actual as (
    select coalesce(sum(net_revenue), 0) as total from {{ ref('mart_sales_daily') }}
), expected as (
    select coalesce(sum(net_amount), 0) as total from {{ ref('stg_orders') }} where status = 'paid'
)
select actual.total as actual_total, expected.total as expected_total
from actual cross join expected
where abs(actual.total - expected.total) > 0.01
