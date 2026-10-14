select
    cast(customer_id as int64) as customer_id,
    customer_name,
    lower(trim(segment)) as segment,
    cast(updated_at as timestamp) as updated_at
from {{ source('demo_raw', 'raw_customers') }}
