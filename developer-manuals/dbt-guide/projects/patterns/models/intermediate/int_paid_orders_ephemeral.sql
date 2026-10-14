-- 小さな1回利用の処理をCTEとして組み込みます。
select order_id, customer_id, order_date, net_amount
from {{ ref('stg_orders') }}
where status = 'paid'
