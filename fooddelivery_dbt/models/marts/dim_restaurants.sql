select
    restaurant_id,
    restaurant_name,
    city,
    cuisine,
    avg_rating,
    is_active
from {{ ref('stg_restaurants') }}