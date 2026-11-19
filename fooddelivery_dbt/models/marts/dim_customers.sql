select
    customer_id,
    customer_name,
    email,
    phone,
    city,
    signup_date
from {{ ref('stg_customers') }}