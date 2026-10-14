{{ config(materialized='incremental', incremental_strategy='merge', unique_key='event_id', on_schema_change='fail') }}
-- イベントは不変という前提。BigQueryのmergeで新規IDを追記します。
-- 全対象とのNOT EXISTS比較は読み取り費用が増えるため、大規模化時は別途最適化します。
select e.event_id, e.order_id, e.event_type, e.event_at
from {{ ref('stg_events') }} as e
{% if is_incremental() %}
where not exists (select 1 from {{ this }} as old where old.event_id = e.event_id)
{% endif %}
