{{
    config(
        materialized='table',
        description='Route-level performance metrics for TGV and Intercités connections'
    )
}}

with route_metrics as (
    select
        route,
        service_type,
        service,
        departure_station,
        arrival_station,

        -- Date range
        min(date) as first_observation_date,
        max(date) as last_observation_date,
        count(distinct date) as days_observed,

        -- Volume aggregations
        sum(planned_trains) as total_trains_planned,
        sum(operated_trains) as total_trains_operated,
        sum(cancelled_trains) as total_trains_cancelled,
        sum(delayed_arrivals) as total_trains_delayed,

        -- TGV-specific metrics
        sum(trains_delayed_over_15min) as total_trains_delayed_over_15min,
        sum(trains_delayed_over_30min) as total_trains_delayed_over_30min,
        sum(trains_delayed_over_60min) as total_trains_delayed_over_60min,

        -- Average metrics
        avg(punctuality_rate) as avg_punctuality_rate,
        avg(cancellation_rate) as avg_cancellation_rate,
        avg(avg_delay_arrival_minutes) as avg_delay_minutes,

        -- Variability metrics
        stddev(punctuality_rate) as stddev_punctuality_rate,
        min(punctuality_rate) as min_punctuality_rate,
        max(punctuality_rate) as max_punctuality_rate

    from {{ ref('fct_train_punctuality') }}
    where service_type in ('TGV', 'Intercités')  -- Route-level data only
    group by 1, 2, 3, 4, 5
)

select

    -- Dimensions
    route,
    service_type,
    service,
    departure_station,
    arrival_station,

    -- Observation window
    first_observation_date,
    last_observation_date,
    days_observed,
    datediff('day', first_observation_date, last_observation_date) + 1 as total_days_in_window,

    -- Volume metrics
    total_trains_planned,
    total_trains_operated,
    total_trains_cancelled,
    total_trains_delayed,
    total_trains_delayed_over_15min,
    total_trains_delayed_over_30min,
    total_trains_delayed_over_60min,

    -- Performance KPIs
    round(avg_punctuality_rate, 2) as avg_punctuality_rate,
    round(avg_cancellation_rate, 2) as avg_cancellation_rate,
    round(avg_delay_minutes, 2) as avg_delay_minutes,

    -- Reliability metrics
    round(stddev_punctuality_rate, 2) as punctuality_rate_std_dev,
    round(min_punctuality_rate, 2) as worst_month_punctuality,
    round(max_punctuality_rate, 2) as best_month_punctuality,

    -- Calculated rates
    case
        when total_trains_planned > 0
        then round(100.0 * total_trains_cancelled / total_trains_planned, 2)
        else null
    end as overall_cancellation_rate,

    case
        when total_trains_operated > 0
        then round(100.0 * total_trains_delayed / total_trains_operated, 2)
        else null
    end as overall_delay_rate,

    case
        when total_trains_operated > 0
        then round(100.0 * (total_trains_operated - total_trains_delayed) / total_trains_operated, 2)
        else null
    end as overall_punctuality_rate,

    -- Severe delays (TGV only, will be null for Intercités)
    case
        when total_trains_operated > 0 and total_trains_delayed_over_15min is not null
        then round(100.0 * total_trains_delayed_over_15min / total_trains_operated, 2)
        else null
    end as severe_delay_rate_15min,

    case
        when total_trains_operated > 0 and total_trains_delayed_over_30min is not null
        then round(100.0 * total_trains_delayed_over_30min / total_trains_operated, 2)
        else null
    end as severe_delay_rate_30min,

    -- Route classification
    case
        when total_trains_operated >= 50000 then 'Major Route'
        when total_trains_operated >= 10000 then 'Important Route'
        when total_trains_operated >= 1000 then 'Regular Route'
        else 'Minor Route'
    end as route_importance,

    case
        when avg_punctuality_rate >= 95 then 'Excellent'
        when avg_punctuality_rate >= 90 then 'Good'
        when avg_punctuality_rate >= 80 then 'Fair'
        when avg_punctuality_rate >= 70 then 'Poor'
        else 'Critical'
    end as performance_rating,

    -- Metadata
    current_timestamp as _dbt_loaded_at

from route_metrics
