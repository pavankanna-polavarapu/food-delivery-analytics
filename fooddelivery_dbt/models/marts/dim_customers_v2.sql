select 
    customer_id,
    customer_name,
    city,
    signup_date
from {{ ref('stg_customers') }}