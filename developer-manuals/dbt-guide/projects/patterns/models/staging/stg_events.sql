select event_id, order_id, event_type, cast(event_at as timestamp) as event_at
from {{ source('demo_raw', 'raw_events') }}
