-- 通常runでは実行されない、確認用のSELECTです。
select 'source_paid_total' as check_name, sum(net_amount) as value
from {{ ref('stg_orders') }} where status = 'paid'
union all
select 'mart_paid_total', sum(net_revenue) from {{ ref('mart_sales_daily') }}
