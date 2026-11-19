{% snapshot snap_restaurants %}

{{
    config(
        target_schema = 'snapshots',
        unique_key = 'restaurant_id',
        strategy = 'timestamp',
        updated_at = 'updated_at',
        invalidate_hard_deletes = True
    )
}}

select * from {{ source("raw", "restaurants") }}

{% endsnapshot %}