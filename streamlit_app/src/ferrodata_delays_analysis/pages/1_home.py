"""
🚄 SNCF Train Punctuality Analytics - Home

Executive overview of French train performance across TGV, TER, and Intercités services.
"""

from datetime import datetime

import streamlit as st

from ferrodata_delays_analysis.components.footer import render_footer
from ferrodata_delays_analysis.utils.database import query_data


def main():
    """Home page with executive dashboard."""

    # Page header
    st.title("🚄 SNCF Train Punctuality Analytics")
    st.markdown("""
    Real-time insights into French train performance across **TGV**, **TER**, and **Intercités** services.
    Data sourced from SNCF Open Data and processed with dbt.
    """)

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        st.markdown("---")

        # Date range filter
        default_start = '2013-01-01'
        default_end = datetime.now()

        date_range = st.date_input(
            "Date Range",
            value=(default_start, default_end),
            help="Select the time period for analysis"
        )

        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = default_start
            end_date = default_end

        # Service type filter
        service_types = st.multiselect(
            "Service Type",
            options=["TGV", "TER", "Intercités"],
            default=["TGV", "TER", "Intercités"],
            help="Select which train services to include"
        )

        st.markdown("---")
        st.info("💡 Use the navigation above to explore detailed analytics")

    # Main dashboard
    st.header("📊 Executive Summary")

    # KPI Cards
    kpi_query = f"""
    SELECT
        SUM(total_operated_trains) as total_trains,
        ROUND(AVG(punctuality_rate), 2) as avg_punctuality,
        ROUND(AVG(cancellation_rate), 2) as avg_cancellation,
        COUNT(DISTINCT month_start_date) as months_analyzed
    FROM analytics_analytics.agg_monthly_service_performance
    WHERE month_start_date BETWEEN '{start_date}' AND '{end_date}'
        AND service_type IN ({','.join([f"'{s}'" for s in service_types])})
    """

    kpi_data = query_data(kpi_query)

    if not kpi_data.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="🚂 Total Trains Operated",
                value=f"{int(kpi_data['total_trains'].iloc[0]):,}",
                help="Total number of trains operated in selected period"
            )

        with col2:
            punctuality = kpi_data['avg_punctuality'].iloc[0]
            st.metric(
                label="⏰ Avg Punctuality Rate",
                value=f"{punctuality}%",
                help="Percentage of trains arriving on time"
            )

        with col3:
            cancellation = kpi_data['avg_cancellation'].iloc[0]
            st.metric(
                label="❌ Avg Cancellation Rate",
                value=f"{cancellation}%",
                help="Percentage of planned trains that were cancelled"
            )

        with col4:
            st.metric(
                label="📅 Analysis Period",
                value=f"{int(kpi_data['months_analyzed'].iloc[0])} months",
                help="Number of months included in this analysis"
            )

    st.markdown("---")

    # Performance trends
    st.subheader("📈 Punctuality Trends by Service Type")

    trends_query = f"""
    SELECT
        month_start_date as date,
        service_type,
        punctuality_rate,
        cancellation_rate,
        total_operated_trains
    FROM analytics_analytics.agg_monthly_service_performance
    WHERE month_start_date BETWEEN '{start_date}' AND '{end_date}'
        AND service_type IN ({','.join([f"'{s}'" for s in service_types])})
    ORDER BY month_start_date, service_type
    """

    trends_data = query_data(trends_query)

    if not trends_data.empty:
        # Punctuality trend
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Punctuality Rate Over Time")
            chart_data = trends_data.pivot(
                index='date',
                columns='service_type',
                values='punctuality_rate'
            ).reset_index()
            st.line_chart(chart_data, x='date', y=service_types)

        with col2:
            st.markdown("#### Cancellation Rate Over Time")
            chart_data = trends_data.pivot(
                index='date',
                columns='service_type',
                values='cancellation_rate'
            ).reset_index()
            st.line_chart(chart_data, x='date', y=service_types)

    st.markdown("---")

    # Service comparison
    st.subheader("🔄 Service Type Comparison")

    comparison_query = f"""
    SELECT
        service_type,
        SUM(total_operated_trains) as trains_operated,
        ROUND(AVG(punctuality_rate), 2) as avg_punctuality,
        ROUND(AVG(cancellation_rate), 2) as avg_cancellation,
        ROUND(AVG(delay_rate), 2) as avg_delay_rate
    FROM analytics_analytics.agg_monthly_service_performance
    WHERE month_start_date BETWEEN '{start_date}' AND '{end_date}'
        AND service_type IN ({','.join([f"'{s}'" for s in service_types])})
    GROUP BY service_type
    ORDER BY avg_punctuality DESC
    """

    comparison_data = query_data(comparison_query)

    if not comparison_data.empty:
        st.dataframe(
            comparison_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "service_type": "Service Type",
                "trains_operated": st.column_config.NumberColumn(
                    "Trains Operated",
                    format="%d"
                ),
                "avg_punctuality": st.column_config.NumberColumn(
                    "Avg Punctuality (%)",
                    format="%.2f%%"
                ),
                "avg_cancellation": st.column_config.NumberColumn(
                    "Avg Cancellation (%)",
                    format="%.2f%%"
                ),
                "avg_delay_rate": st.column_config.NumberColumn(
                    "Avg Delay Rate (%)",
                    format="%.2f%%"
                ),
            }
        )

    st.markdown("---")

    # Recent top/bottom performers
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Best Performing Routes")
        best_routes_query = """
        SELECT
            route,
            service_type,
            ROUND(overall_punctuality_rate, 2) as punctuality_rate,
            total_trains_operated as trains
        FROM analytics_analytics.agg_route_performance
        WHERE total_trains_operated > 500
        ORDER BY overall_punctuality_rate DESC
        LIMIT 5
        """
        best_routes = query_data(best_routes_query)

        if not best_routes.empty:
            st.dataframe(
                best_routes,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "route": "Route",
                    "service_type": "Service",
                    "punctuality_rate": st.column_config.NumberColumn(
                        "Punctuality",
                        format="%.2f%%"
                    ),
                    "trains": st.column_config.NumberColumn(
                        "Trains",
                        format="%d"
                    ),
                }
            )

    with col2:
        st.subheader("⚠️ Routes Needing Attention")
        worst_routes_query = """
        SELECT
            route,
            service_type,
            ROUND(overall_punctuality_rate, 2) as punctuality_rate,
            total_trains_operated as trains
        FROM analytics_analytics.agg_route_performance
        WHERE total_trains_operated > 500
        ORDER BY overall_punctuality_rate ASC
        LIMIT 5
        """
        worst_routes = query_data(worst_routes_query)

        if not worst_routes.empty:
            st.dataframe(
                worst_routes,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "route": "Route",
                    "service_type": "Service",
                    "punctuality_rate": st.column_config.NumberColumn(
                        "Punctuality",
                        format="%.2f%%"
                    ),
                    "trains": st.column_config.NumberColumn(
                        "Trains",
                        format="%d"
                    ),
                }
            )

    # Footer
    render_footer()

if __name__ == "__main__":
    main()
