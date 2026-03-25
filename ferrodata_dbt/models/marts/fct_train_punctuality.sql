{{
    config(
        materialized='table',
        description='Unified fact table for train punctuality across all services (TGV, TER, Intercités)'
    )
}}

-- TGV data (most detailed, route-level)
with tgv_punctuality as (
    select
        'TGV' as service_type,
        date,
        service,
        departure_station,
        arrival_station,
        departure_station || ' → ' || arrival_station as route,

        -- Volume metrics
        planned_trains,
        cancelled_trains,
        planned_trains - cancelled_trains as operated_trains,

        -- Delay metrics (arrivals are primary KPI)
        delayed_arrivals,
        avg_delay_arrival_minutes,
        trains_delayed_over_15min,
        trains_delayed_over_30min,
        trains_delayed_over_60min,

        -- Performance metrics
        case
            when planned_trains > 0
            then round(100.0 * (planned_trains - delayed_arrivals) / planned_trains, 2)
            else null
        end as punctuality_rate,

        case
            when planned_trains > 0
            then round(100.0 * cancelled_trains / planned_trains, 2)
            else null
        end as cancellation_rate,

        -- Metadata
        _loaded_at as source_loaded_at
    from {{ ref('stg_sncf__regularite_tgv') }}
),

-- TER data (regional, aggregated by region)
ter_punctuality as (
    select
        'TER' as service_type,
        date,
        region as service,
        region as departure_station,  -- TER doesn't have route detail
        region as arrival_station,
        region as route,

        -- Volume metrics
        planned_trains,
        cancelled_trains,
        operated_trains,

        -- Delay metrics
        delayed_arrivals,
        null as avg_delay_arrival_minutes,  -- Not provided in TER data
        null as trains_delayed_over_15min,
        null as trains_delayed_over_30min,
        null as trains_delayed_over_60min,

        -- Performance metrics
        punctuality_rate,
        case
            when planned_trains > 0
            then round(100.0 * cancelled_trains / planned_trains, 2)
            else null
        end as cancellation_rate,

        -- Metadata
        _loaded_at as source_loaded_at
    from {{ ref('stg_sncf__regularite_ter') }}
),

-- Intercités data (route-level like TGV)
intercites_punctuality as (
    select
        'Intercités' as service_type,
        date,
        'National' as service,  -- Intercités doesn't distinguish service types
        departure_station,
        arrival_station,
        departure_station || ' → ' || arrival_station as route,

        -- Volume metrics
        planned_trains,
        cancelled_trains,
        operated_trains,

        -- Delay metrics
        delayed_arrivals,
        null as avg_delay_arrival_minutes,  -- Not provided
        null as trains_delayed_over_15min,
        null as trains_delayed_over_30min,
        null as trains_delayed_over_60min,

        -- Performance metrics
        punctuality_rate,
        case
            when planned_trains > 0
            then round(100.0 * cancelled_trains / planned_trains, 2)
            else null
        end as cancellation_rate,

        -- Metadata
        _loaded_at as source_loaded_at
    from {{ ref('stg_sncf__regularite_intercites') }}
),

-- Union all services
unified as (
    select * from tgv_punctuality
    union all
    select * from ter_punctuality
    union all
    select * from intercites_punctuality
)

select

    -- Dimensions
    service_type,
    date,
    extract(year from date) as year,
    extract(month from date) as month,
    extract(quarter from date) as quarter,
    service,
    departure_station,
    arrival_station,
    route,

    -- Volume metrics
    planned_trains,
    cancelled_trains,
    operated_trains,

    -- Delay metrics
    delayed_arrivals,
    avg_delay_arrival_minutes,
    trains_delayed_over_15min,
    trains_delayed_over_30min,
    trains_delayed_over_60min,

    -- Performance KPIs
    punctuality_rate,
    cancellation_rate,

    -- Derived metrics
    case
        when operated_trains > 0
        then round(100.0 * delayed_arrivals / operated_trains, 2)
        else null
    end as delay_rate,

    -- Metadata
    source_loaded_at,
    current_timestamp as _dbt_loaded_at

from unified
