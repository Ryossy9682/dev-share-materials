-- 粒度：order_idごとに1行。金額計算と状態名の正規化をここで定義します。
select
    cast(order_id as int64) as order_id,
    cast(customer_id as int64) as customer_id,
    cast(order_date as date) as order_date,
    cast(amount as numeric) as amount,
    cast(discount_rate as numeric) as discount_rate,
    {{ net_amount('amount', 'discount_rate') }} as net_amount,
    lower(trim(status)) as status,
    cast(updated_at as timestamp) as updated_at
from {{ source('demo_raw', 'raw_orders') }}
