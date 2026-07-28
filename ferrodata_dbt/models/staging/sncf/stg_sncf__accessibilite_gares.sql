with source as (
    select *
    from {{ source('sncf', 'equipements_accessibilite_gares') }}
)

select
    uic as uic_code,
    lower(replace(nom_de_la_gare, '-', ' ')) as station_name,
    adresse as address,
    codepostal as postal_code,
    ville as city,
    accessibilite as accessibility_equipment,
    current_timestamp as _loaded_at
from source
