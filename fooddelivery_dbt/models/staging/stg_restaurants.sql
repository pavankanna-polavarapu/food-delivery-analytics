select 
    restaurant_id,
    restaurant_name,
    city,
    cuisine,
    avg_rating,
    is_active,
    updated_at
from {{ source('raw', 'restaurants')}}