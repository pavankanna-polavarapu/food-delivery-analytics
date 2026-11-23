select
    restaurant_id,
    restaurant_name,
    city,
    cuisine,
    {{ clean_string('cuisine') }} as cuisine_type_cleaned,
    avg_rating,
    is_active
from {{ ref('stg_restaurants') }}