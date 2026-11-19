select
    partner_id,
    partner_name,
    city,
    vehicle_type,
    joined_date
from {{ ref('stg_delivery_partners') }}