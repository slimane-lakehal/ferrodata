with source as (
    select *
    from {{ source('sncf', 'regularite_tgv') }}
)

select
    -- Primary identifiers
    date,
    service,
    gare_depart as departure_station,
    gare_arrivee as arrival_station,

    -- Trip metrics
    duree_moyenne as avg_duration_minutes,

    -- Planned trains
    nb_train_prevu as planned_trains,

    -- Cancellations
    nb_annulation as cancelled_trains,
    commentaire_annulation as cancellation_comment,

    -- Departure delays
    nb_train_depart_retard as delayed_departures,
    retard_moyen_depart as avg_delay_departure_minutes,
    retard_moyen_tous_trains_depart as avg_delay_all_trains_departure_minutes,
    commentaire_retards_depart as delay_departure_comment,

    -- Arrival delays
    nb_train_retard_arrivee as delayed_arrivals,
    retard_moyen_arrivee as avg_delay_arrival_minutes,
    retard_moyen_tous_trains_arrivee as avg_delay_all_trains_arrival_minutes,
    commentaires_retard_arrivee as delay_arrival_comment,

    -- Significant delays
    nb_train_retard_sup_15 as trains_delayed_over_15min,
    retard_moyen_trains_retard_sup15 as avg_delay_trains_over_15min,
    nb_train_retard_sup_30 as trains_delayed_over_30min,
    nb_train_retard_sup_60 as trains_delayed_over_60min,

    -- Delay causes (percentages)
    prct_cause_externe as pct_delay_external_cause,
    prct_cause_infra as pct_delay_infrastructure,
    prct_cause_gestion_trafic as pct_delay_traffic_management,
    prct_cause_materiel_roulant as pct_delay_rolling_stock,
    prct_cause_gestion_gare as pct_delay_station_management,
    prct_cause_prise_en_charge_voyageurs as pct_delay_passenger_handling,

    -- Metadata
    current_timestamp as _loaded_at
from source
