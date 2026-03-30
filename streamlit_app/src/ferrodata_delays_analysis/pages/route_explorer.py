"""
🚄 Route Explorer

Compare and analyze individual train routes with detailed performance metrics.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from ferrodata_delays_analysis.components.footer import render_footer
from ferrodata_delays_analysis.utils.database import MART_SCHEMA, get_all_routes, query_data


def main():
    """Route explorer page."""

    st.title("🚄 Route Explorer")
    st.markdown("""
    Deep dive into specific train routes. Compare performance, analyze trends,
    and identify operational patterns.
    """)

    # Sidebar - Route selection
    with st.sidebar:
        st.header("🔍 Route Selection")

        # Get all available routes
        all_routes = get_all_routes()

        if not all_routes:
            st.error("❌ No route data available")
            st.stop()

        # Route selector
        selected_routes = st.multiselect(
            "Select Routes to Compare",
            options=all_routes,
            default=all_routes[:3] if len(all_routes) >= 3 else all_routes,
            help="Select up to 5 routes to compare",
            max_selections=5,
        )

        if not selected_routes:
            st.info("👈 Select at least one route from the sidebar to begin analysis")
            st.stop()

        st.markdown("---")

        # Service type filter
        service_filter = st.multiselect(
            "Service Type",
            options=["TGV", "Intercités"],
            default=["TGV", "Intercités"],
            help="Filter by train service type",
        )

    # Fetch route performance data
    route_query = f"""
    SELECT
        route,
        service_type,
        departure_station,
        arrival_station,
        total_trains_operated,
        total_trains_cancelled,
        total_trains_delayed,
        overall_punctuality_rate,
        overall_cancellation_rate,
        overall_delay_rate,
        avg_delay_minutes,
        severe_delay_rate_15min,
        severe_delay_rate_30min,
        route_importance,
        performance_rating,
        first_observation_date,
        last_observation_date,
        days_observed
    FROM {MART_SCHEMA}.agg_route_performance
    WHERE route IN ({",".join([f"'{r}'" for r in selected_routes])})
        AND service_type IN ({",".join([f"'{s}'" for s in service_filter])})
    ORDER BY overall_punctuality_rate DESC
    """

    route_data = query_data(route_query)

    if route_data.empty:
        st.warning("⚠️ No data available for selected routes")
        st.stop()

    # Overview metrics
    st.header("📊 Route Comparison Overview")

    # Display key metrics
    for idx, row in route_data.iterrows():
        with st.expander(f"🚄 {row['route']} ({row['service_type']})", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric(
                    "Punctuality",
                    f"{row['overall_punctuality_rate']:.1f}%",
                    help="Overall punctuality rate",
                )

            with col2:
                st.metric(
                    "Trains Operated",
                    f"{int(row['total_trains_operated']):,}",
                    help="Total trains operated on this route",
                )

            with col3:
                st.metric(
                    "Cancellation Rate",
                    f"{row['overall_cancellation_rate']:.2f}%",
                    help="Percentage of trains cancelled",
                )

            with col4:
                st.metric(
                    "Avg Delay",
                    f"{row['avg_delay_minutes']:.1f} min"
                    if pd.notna(row["avg_delay_minutes"])
                    else "N/A",
                    help="Average delay in minutes",
                )

            with col5:
                # Performance rating with color
                rating = row["performance_rating"]
                rating_colors = {
                    "Excellent": "🟢",
                    "Good": "🟡",
                    "Fair": "🟠",
                    "Poor": "🔴",
                    "Critical": "⚫",
                }
                st.metric(
                    "Rating",
                    f"{rating_colors.get(rating, '')} {rating}",
                    help="Performance rating based on punctuality",
                )

            # Additional details
            st.markdown(f"""
            **Route Details:**
            - From: {row["departure_station"]}
            - To: {row["arrival_station"]}
            - Importance: {row["route_importance"]}
            - Observation Period: {row["first_observation_date"]} to {row["last_observation_date"]}
            - Days Observed: {row["days_observed"]}
            """)

    st.markdown("---")

    # Comparison charts
    st.header("📈 Performance Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Punctuality vs Delay Rate")
        fig = px.scatter(
            route_data,
            x="overall_delay_rate",
            y="overall_punctuality_rate",
            size="total_trains_operated",
            color="service_type",
            hover_name="route",
            labels={
                "overall_delay_rate": "Delay Rate (%)",
                "overall_punctuality_rate": "Punctuality Rate (%)",
                "total_trains_operated": "Trains Operated",
            },
            title="Punctuality vs Delay Rate (sized by volume)",
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Cancellation Rate Comparison")
        fig = px.bar(
            route_data,
            x="route",
            y="overall_cancellation_rate",
            color="performance_rating",
            hover_data=["total_trains_cancelled", "total_trains_operated"],
            labels={"overall_cancellation_rate": "Cancellation Rate (%)"},
            title="Cancellation Rate by Route",
        )
        fig.update_layout(template="plotly_white", xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Time series analysis (if single route selected)
    if len(selected_routes) == 1:
        st.header("📅 Historical Performance Trends")

        route = selected_routes[0]

        # Fetch monthly data for the selected route
        monthly_query = f"""
        SELECT
            date,
            extract(year from date) as year,
            extract(month from date) as month,
            punctuality_rate,
            cancellation_rate,
            planned_trains,
            operated_trains,
            delayed_arrivals
        FROM {MART_SCHEMA}.fct_train_punctuality
        WHERE route = '{route}'
        ORDER BY date
        """

        monthly_data = query_data(monthly_query)

        if not monthly_data.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Punctuality Over Time")
                fig = px.line(
                    monthly_data,
                    x="date",
                    y="punctuality_rate",
                    markers=True,
                    labels={"punctuality_rate": "Punctuality Rate (%)"},
                    title=f"{route} - Punctuality Trend",
                )
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Train Volume Over Time")
                fig = px.bar(
                    monthly_data,
                    x="date",
                    y="operated_trains",
                    labels={"operated_trains": "Trains Operated"},
                    title=f"{route} - Monthly Train Volume",
                )
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            # Seasonal patterns
            monthly_avg = (
                monthly_data.groupby("month")
                .agg({"punctuality_rate": "mean", "operated_trains": "mean"})
                .reset_index()
            )

            month_names = [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ]
            monthly_avg["month_name"] = monthly_avg["month"].apply(
                lambda x: month_names[int(x) - 1]
            )

            st.subheader("📊 Seasonal Patterns")

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    monthly_avg,
                    x="month_name",
                    y="punctuality_rate",
                    labels={"punctuality_rate": "Avg Punctuality (%)"},
                    title="Average Punctuality by Month",
                )
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.bar(
                    monthly_avg,
                    x="month_name",
                    y="operated_trains",
                    labels={"operated_trains": "Avg Trains"},
                    title="Average Train Volume by Month",
                )
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Detailed data table
    st.header("📋 Detailed Route Data")

    st.dataframe(
        route_data[
            [
                "route",
                "service_type",
                "performance_rating",
                "total_trains_operated",
                "overall_punctuality_rate",
                "overall_cancellation_rate",
                "overall_delay_rate",
                "avg_delay_minutes",
                "route_importance",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "route": "Route",
            "service_type": "Service",
            "performance_rating": "Rating",
            "total_trains_operated": st.column_config.NumberColumn("Trains", format="%d"),
            "overall_punctuality_rate": st.column_config.NumberColumn(
                "Punctuality", format="%.2f%%"
            ),
            "overall_cancellation_rate": st.column_config.NumberColumn(
                "Cancellation", format="%.2f%%"
            ),
            "overall_delay_rate": st.column_config.NumberColumn("Delay Rate", format="%.2f%%"),
            "avg_delay_minutes": st.column_config.NumberColumn("Avg Delay (min)", format="%.1f"),
            "route_importance": "Importance",
        },
    )

    # Download option
    csv = route_data.to_csv(index=False)
    st.download_button(
        label="📥 Download Route Data (CSV)",
        data=csv,
        file_name="sncf_route_analysis.csv",
        mime="text/csv",
    )

    # Footer
    st.markdown("---")
    render_footer()


if __name__ == "__main__":
    main()
