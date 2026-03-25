with source as (
    select *
    from {{ source('sncf', 'regularite_ter') }}
)

select
    -- Primary identifiers
    date,
    lower(replace(region, '-', ' ')) as region,

    -- Train volumes
    nombre_de_trains_programmes as planned_trains,
    nombre_de_trains_ayant_circule as operated_trains,
    nombre_de_trains_annules as cancelled_trains,

    -- Delays
    nombre_de_trains_en_retard_a_l_arrivee as delayed_arrivals,

    -- Performance metrics
    taux_de_regularite as punctuality_rate,
    nombre_de_trains_a_l_heure_pour_un_train_en_retard_a_l_arrivee as on_time_trains_per_delayed_train,

    -- Comments
    commentaires as comments,

    -- Metadata
    current_timestamp as _loaded_at
from source
