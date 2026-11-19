select 
    partner_id,
    partner_name,
    city,
    vehicle_type,
    joined_date
from {{ source( 'raw', 'delivery_partners')}}