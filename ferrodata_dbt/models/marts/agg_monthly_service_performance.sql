{{
    config(
        materialized='table',
        description='Monthly aggregated performance metrics by service type'
    )
}}

with monthly_metrics as (
    select
        {{date_trunc('month', 'date')}} as month_start_date,
        extract(year from date) as year,
        extract(month from date) as month,
        service_type,

        -- Volume aggregations
        sum(planned_trains) as total_planned_trains,
        sum(cancelled_trains) as total_cancelled_trains,
        sum(operated_trains) as total_operated_trains,
        sum(delayed_arrivals) as total_delayed_arrivals,

        -- TGV-specific aggregations (nulls for TER/Intercités)
        sum(trains_delayed_over_15min) as total_trains_delayed_over_15min,
        sum(trains_delayed_over_30min) as total_trains_delayed_over_30min,
        sum(trains_delayed_over_60min) as total_trains_delayed_over_60min,

        -- Count distinct routes/regions served
        count(distinct route) as unique_routes_served,

        -- Record count
        count(*) as total_records

    from {{ ref('fct_train_punctuality') }}
    group by 1, 2, 3, 4
)

select
    -- Dimensions
    month_start_date,
    year,
    month,
    case month
        when 1 then 'January'
        when 2 then 'February'
        when 3 then 'March'
        when 4 then 'April'
        when 5 then 'May'
        when 6 then 'June'
        when 7 then 'July'
        when 8 then 'August'
        when 9 then 'September'
        when 10 then 'October'
        when 11 then 'November'
        when 12 then 'December'
    end as month_name,
    service_type,

    -- Volume metrics
    total_planned_trains,
    total_cancelled_trains,
    total_operated_trains,
    total_delayed_arrivals,
    total_trains_delayed_over_15min,
    total_trains_delayed_over_30min,
    total_trains_delayed_over_60min,

    -- Operational metrics
    unique_routes_served,
    total_records as route_month_records,

    -- Calculated KPIs
    case
        when total_planned_trains > 0
        then round(100.0 * total_cancelled_trains / total_planned_trains, 2)
        else null
    end as cancellation_rate,

    case
        when total_operated_trains > 0
        then round(100.0 * total_delayed_arrivals / total_operated_trains, 2)
        else null
    end as delay_rate,

    case
        when total_operated_trains > 0
        then round(100.0 * (total_operated_trains - total_delayed_arrivals) / total_operated_trains, 2)
        else null
    end as punctuality_rate,

    -- Severe delay metrics (TGV only, will be null for others)
    case
        when total_operated_trains > 0 and total_trains_delayed_over_15min is not null
        then round(100.0 * total_trains_delayed_over_15min / total_operated_trains, 2)
        else null
    end as severe_delay_rate_15min,

    case
        when total_operated_trains > 0 and total_trains_delayed_over_30min is not null
        then round(100.0 * total_trains_delayed_over_30min / total_operated_trains, 2)
        else null
    end as severe_delay_rate_30min,

    -- Metadata
    current_timestamp as _dbt_loaded_at

from monthly_metrics
order by month_start_date, service_type
