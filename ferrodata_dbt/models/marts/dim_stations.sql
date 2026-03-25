{{
    config(
        materialized='table',
        description='Station master dimension with geography and metadata'
    )
}}

with stations as (
    select
        uic_code,
        station_name,
        city,
        departement,
        lon,
        lat,
        fret as freight_service,
        passengers as passenger_service,
        line_code,
        track_number,
        kilometer_point,
        network_id,
        _loaded_at
    from {{ ref('stg_sncf__gares') }}
),

-- Classify stations by size/importance based on route appearances
station_activity as (
    select
        departure_station as station_name,
        count(distinct date) as days_active_departure,
        sum(planned_trains) as total_trains_departed
    from {{ ref('stg_sncf__regularite_tgv') }}
    group by 1

    union all

    select
        arrival_station as station_name,
        count(distinct date) as days_active_arrival,
        sum(planned_trains) as total_trains_arrived
    from {{ ref('stg_sncf__regularite_tgv') }}
    group by 1

    union all

    select
        departure_station as station_name,
        count(distinct date) as days_active,
        sum(planned_trains) as total_trains
    from {{ ref('stg_sncf__regularite_intercites') }}
    group by 1

    union all

    select
        arrival_station as station_name,
        count(distinct date) as days_active,
        sum(planned_trains) as total_trains
    from {{ ref('stg_sncf__regularite_intercites') }}
    group by 1
),

station_usage as (
    select
        station_name,
        sum(days_active_departure) as total_days_active,
        sum(total_trains_departed) as total_trains_handled
    from station_activity
    group by 1
),

station_classification as (
    select
        station_name,
        total_days_active,
        total_trains_handled,
        case
            when total_trains_handled >= 50000 then 'Major Hub'
            when total_trains_handled >= 10000 then 'Regional Hub'
            when total_trains_handled >= 1000 then 'Medium Station'
            when total_trains_handled > 0 then 'Small Station'
            else 'Inactive/Freight Only'
        end as station_tier
    from station_usage
)

select
    s.uic_code as station_id,
    s.station_name,
    s.city,
    s.departement as department,
    s.lon as longitude,
    s.lat as latitude,

    -- Service flags
    case when s.freight_service = 'O' then true else false end as has_freight_service,
    case when s.passenger_service = 'O' then true else false end as has_passenger_service,

    -- Infrastructure metadata
    s.line_code,
    s.track_number as section_rank,
    s.kilometer_point,
    s.network_id,

    -- Activity metrics
    coalesce(sc.total_days_active, 0) as total_days_active,
    coalesce(sc.total_trains_handled, 0) as total_trains_handled,
    coalesce(sc.station_tier, 'Inactive/Freight Only') as station_tier,

    -- Metadata
    s._loaded_at as source_loaded_at,
    current_timestamp as _dbt_loaded_at

from stations s
left join station_classification sc
    on s.station_name = sc.station_name
