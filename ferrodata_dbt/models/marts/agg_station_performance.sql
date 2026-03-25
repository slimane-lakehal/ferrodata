{{
    config(
        materialized='table',
        description='Station-level performance aggregations for departures and arrivals'
    )
}}

-- Aggregate departures by station
with departure_performance as (
    select
        departure_station as station_name,
        service_type,

        count(*) as total_departure_records,
        sum(planned_trains) as total_departures_planned,
        sum(operated_trains) as total_departures_operated,
        sum(cancelled_trains) as total_departures_cancelled,
        sum(delayed_arrivals) as total_delays_from_this_station,

        -- Averages
        avg(punctuality_rate) as avg_departure_punctuality_rate,
        avg(cancellation_rate) as avg_departure_cancellation_rate

    from {{ ref('fct_train_punctuality') }}
    where departure_station is not null
    group by 1, 2
),

-- Aggregate arrivals by station
arrival_performance as (
    select
        arrival_station as station_name,
        service_type,

        count(*) as total_arrival_records,
        sum(planned_trains) as total_arrivals_planned,
        sum(operated_trains) as total_arrivals_operated,
        sum(cancelled_trains) as total_arrivals_cancelled,
        sum(delayed_arrivals) as total_delays_at_this_station,

        -- Averages
        avg(punctuality_rate) as avg_arrival_punctuality_rate,
        avg(cancellation_rate) as avg_arrival_cancellation_rate

    from {{ ref('fct_train_punctuality') }}
    where arrival_station is not null
    group by 1, 2
),

-- Combine departure and arrival metrics
combined_performance as (
    select
        coalesce(d.station_name, a.station_name) as station_name,
        coalesce(d.service_type, a.service_type) as service_type,

        -- Departure metrics
        coalesce(d.total_departure_records, 0) as total_departure_records,
        coalesce(d.total_departures_planned, 0) as total_departures_planned,
        coalesce(d.total_departures_operated, 0) as total_departures_operated,
        coalesce(d.total_departures_cancelled, 0) as total_departures_cancelled,
        coalesce(d.total_delays_from_this_station, 0) as total_delays_from_station,
        d.avg_departure_punctuality_rate,
        d.avg_departure_cancellation_rate,

        -- Arrival metrics
        coalesce(a.total_arrival_records, 0) as total_arrival_records,
        coalesce(a.total_arrivals_planned, 0) as total_arrivals_planned,
        coalesce(a.total_arrivals_operated, 0) as total_arrivals_operated,
        coalesce(a.total_arrivals_cancelled, 0) as total_arrivals_cancelled,
        coalesce(a.total_delays_at_this_station, 0) as total_delays_at_station,
        a.avg_arrival_punctuality_rate,
        a.avg_arrival_cancellation_rate

    from departure_performance d
    full outer join arrival_performance a
        on d.station_name = a.station_name
        and d.service_type = a.service_type
),
combined_performance_enriched as (

select

    -- Dimensions
    station_name,
    service_type,

    -- Total activity
    total_departure_records + total_arrival_records as total_station_records,
    total_departures_planned + total_arrivals_planned as total_trains_planned,
    total_departures_operated + total_arrivals_operated as total_trains_operated,
    total_departures_cancelled + total_arrivals_cancelled as total_trains_cancelled,

    -- Departure metrics
    total_departure_records,
    total_departures_planned,
    total_departures_operated,
    total_departures_cancelled,
    total_delays_from_station,
    round(avg_departure_punctuality_rate, 2) as avg_departure_punctuality_rate,
    round(avg_departure_cancellation_rate, 2) as avg_departure_cancellation_rate,

    -- Arrival metrics
    total_arrival_records,
    total_arrivals_planned,
    total_arrivals_operated,
    total_arrivals_cancelled,
    total_delays_at_station,
    round(avg_arrival_punctuality_rate, 2) as avg_arrival_punctuality_rate,
    round(avg_arrival_cancellation_rate, 2) as avg_arrival_cancellation_rate

    from combined_performance)

    SELECT * ,

    -- Overall station performance
    case
        when (total_departures_operated + total_arrivals_operated) > 0
        then round(
            100.0 * ((total_departures_operated + total_arrivals_operated) - (total_delays_from_station + total_delays_at_station))
            / (total_departures_operated + total_arrivals_operated),
            2
        )
        else null
    end as overall_punctuality_rate,

    case
        when (total_trains_planned) > 0
        then round(100.0 * total_trains_cancelled / total_trains_planned, 2)
        else null
    end as overall_cancellation_rate,

    -- Station classification
    case
        when total_trains_operated >= 100000 then 'Very High Volume'
        when total_trains_operated >= 50000 then 'High Volume'
        when total_trains_operated >= 10000 then 'Medium Volume'
        when total_trains_operated >= 1000 then 'Low Volume'
        else 'Minimal Volume'
    end as volume_category,

    -- Metadata
    current_timestamp as _dbt_loaded_at

from combined_performance_enriched
