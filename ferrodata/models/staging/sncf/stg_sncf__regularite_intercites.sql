with source as (
    select *
    from {{ source('sncf', 'regularite_intercites') }}
)

select
    date,
    depart as departure_station,
    arrivee as arrival_station,

    nombre_de_trains_programmes as planned_trains,
    nombre_de_trains_ayant_circule as operated_trains,
    nombre_de_trains_annules as cancelled_trains,

    nombre_de_trains_en_retard_a_l_arrivee as delayed_arrivals,

    taux_de_regularite as punctuality_rate,
    nombre_de_trains_a_l_heure_pour_un_train_en_retard_a_l_arrivee as on_time_trains_per_delayed_train,
    current_timestamp as _loaded_at
from source
