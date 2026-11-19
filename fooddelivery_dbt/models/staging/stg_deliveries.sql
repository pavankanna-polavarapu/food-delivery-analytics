with source as (
    select * from {{ source('raw', 'deliveries')}}
)

select 
    delivery_id,
    order_id,
    partner_id,
    pickup_ts,
    delivered_ts,
    distance_km,
    promised_minutes,
    datediff('minute', pickup_ts, delivered_ts) as delivery_minutes,
    delivered_ts < pickup_ts as has_invalid_timestamps
from source