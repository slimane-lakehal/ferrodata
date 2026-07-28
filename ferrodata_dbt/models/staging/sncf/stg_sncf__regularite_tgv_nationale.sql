with source as (
    select *
    from {{ source('sncf', 'regularite_tgv_nationale') }}
)

select
    date,
    regularite_composite as composite_regularity_rate,
    ponctualite_origine as departure_punctuality_rate,
    current_timestamp as _loaded_at
from source
