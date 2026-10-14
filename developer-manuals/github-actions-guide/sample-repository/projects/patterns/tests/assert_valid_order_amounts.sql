-- Data test：問題行を返したら失敗します。
select order_id
from {{ ref('stg_orders') }}
where amount < 0 or discount_rate < 0 or discount_rate > 1 or net_amount < 0
