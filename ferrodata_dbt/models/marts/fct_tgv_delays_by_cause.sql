{{
    config(
        materialized='table',
        description='TGV delay root cause analysis - only TGV data has cause breakdown'
    )
}}

with tgv_data as (
    select
        date,
        service,
        departure_station,
        arrival_station,
        departure_station || ' → ' || arrival_station as route,

        -- Total delays to calculate absolute values from percentages
        delayed_arrivals,
        trains_delayed_over_15min,

        -- Cause percentages (from staging table)
        pct_delay_external_cause,
        pct_delay_infrastructure,
        pct_delay_traffic_management,
        pct_delay_rolling_stock,
        pct_delay_station_management,
        pct_delay_passenger_handling,

        _loaded_at
    from {{ ref('stg_sncf__regularite_tgv') }}
    where delayed_arrivals > 0  -- Only include records with actual delays
),

-- Unpivot the cause percentages
causes_unpivoted as (
    select
        date,
        service,
        departure_station,
        arrival_station,
        route,
        delayed_arrivals,
        trains_delayed_over_15min,
        'External Causes' as delay_cause_category,
        'Weather, obstacles, suspicious packages, vandalism, strikes' as cause_description,
        pct_delay_external_cause as cause_percentage,
        _loaded_at
    from tgv_data
    where pct_delay_external_cause is not null

    union all

    select
        date,
        service,
        departure_station,
        arrival_station,
        route,
        delayed_arrivals,
        trains_delayed_over_15min,
        'Infrastructure',
        'Rail infrastructure maintenance and construction work',
        pct_delay_infrastructure,
        _loaded_at
    from tgv_data
    where pct_delay_infrastructure is not null

    union all

    select
        date,
        service,
        departure_station,
        arrival_station,
        route,
        delayed_arrivals,
        trains_delayed_over_15min,
        'Traffic Management',
        'Rail network circulation and network interactions',
        pct_delay_traffic_management,
        _loaded_at
    from tgv_data
    where pct_delay_traffic_management is not null

    union all

    select
        date,
        service,
        departure_station,
        arrival_station,
        route,
        delayed_arrivals,
        trains_delayed_over_15min,
        'Rolling Stock',
        'Train equipment and material issues',
        pct_delay_rolling_stock,
        _loaded_at
    from tgv_data
    where pct_delay_rolling_stock is not null

    union all

    select
        date,
        service,
        departure_station,
        arrival_station,
        route,
        delayed_arrivals,
        trains_delayed_over_15min,
        'Station Management',
        'Station operations and equipment reuse',
        pct_delay_station_management,
        _loaded_at
    from tgv_data
    where pct_delay_station_management is not null

    union all

    select
        date,
        service,
        departure_station,
        arrival_station,
        route,
        delayed_arrivals,
        trains_delayed_over_15min,
        'Passenger Handling',
        'Passenger volume, accessibility services, connections',
        pct_delay_passenger_handling,
        _loaded_at
    from tgv_data
    where pct_delay_passenger_handling is not null
)

select

    -- Dimensions
    date,
    extract(year from date) as year,
    extract(month from date) as month,
    extract(quarter from date) as quarter,
    service,
    departure_station,
    arrival_station,
    route,

    -- Cause details
    delay_cause_category,
    cause_description,

    -- Metrics
    delayed_arrivals as total_delayed_trains,
    trains_delayed_over_15min as total_trains_delayed_over_15min,
    cause_percentage,

    -- Estimated absolute impact (percentage applied to total delays)
    round(delayed_arrivals * (cause_percentage / 100.0), 2) as estimated_trains_delayed_by_cause,

    -- Metadata
    _loaded_at as source_loaded_at,
    current_timestamp as _dbt_loaded_at

from causes_unpivoted
where cause_percentage > 0  -- Only include non-zero causes
