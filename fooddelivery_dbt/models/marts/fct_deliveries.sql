{{ config(materialized='table') }}

-- Grain: one row per delivery with valid timestamps

select
    delivery_id,
    order_id,
    partner_id,
    restaurant_id,
    restaurant_city,
    cast(pickup_ts as date)                          as delivery_date,
    pickup_ts,
    delivered_ts,
    distance_km,
    promised_minutes,
    delivery_minutes,
    is_late_delivery,
    greatest(delivery_minutes - promised_minutes, 0) as minutes_over_sla,
    {{ audit_columns() }}
from {{ ref('int_orders_enriched') }}
where is_valid_order
  and delivery_id is not null