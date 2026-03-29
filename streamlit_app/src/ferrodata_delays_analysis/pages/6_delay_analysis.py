"""
🔍 Delay Root Cause Analysis

Analyze TGV delay causes and identify patterns in operational disruptions.
"""

import plotly.express as px
import streamlit as st

from ferrodata_delays_analysis.components.footer import render_footer
from ferrodata_delays_analysis.utils.database import query_data


def main():
    """Delay root cause analysis page."""

    st.title("🔍 Delay Root Cause Analysis")
    st.markdown("""
    Understand the primary causes of TGV train delays. This analysis helps identify
    operational bottlenecks and improvement opportunities.
    """)

    st.info("ℹ️ **Note:** Detailed delay cause data is only available for TGV services.")

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Analysis Filters")

        # Date range
        year_query = """
        SELECT DISTINCT year
        FROM analytics_analytics.fct_tgv_delays_by_cause
        ORDER BY year DESC
        """
        available_years = query_data(year_query)

        if available_years.empty:
            st.error("❌ No delay cause data available")
            st.stop()

        selected_years = st.multiselect(
            "Select Years",
            options=available_years['year'].tolist(),
            default=[available_years['year'].iloc[0]],  # Default to most recent year
            help="Choose which years to include in analysis"
        )

        if not selected_years:
            st.warning("⚠️ Please select at least one year")
            st.stop()

        # Route filter (optional)
        route_filter = st.text_input(
            "Filter by Route (optional)",
            placeholder="e.g., PARIS",
            help="Enter station name to filter routes"
        )

        st.markdown("---")

    # Fetch delay cause data
    where_clause = f"year IN ({','.join(map(str, selected_years))})"
    if route_filter:
        where_clause += f" AND (route LIKE '%{route_filter}%' OR departure_station LIKE '%{route_filter}%' OR arrival_station LIKE '%{route_filter}%')"

    delay_query = f"""
    SELECT
        delay_cause_category,
        cause_description,
        COUNT(*) as occurrences,
        SUM(estimated_trains_delayed_by_cause) as total_trains_impacted,
        AVG(cause_percentage) as avg_cause_percentage,
        SUM(total_delayed_trains) as total_delayed_trains
    FROM analytics_analytics.fct_tgv_delays_by_cause
    WHERE {where_clause}
    GROUP BY delay_cause_category, cause_description
    ORDER BY total_trains_impacted DESC
    """

    delay_data = query_data(delay_query)

    if delay_data.empty:
        st.warning("⚠️ No delay data matches your filters")
        st.stop()

    # Calculate totals
    total_impact = delay_data['total_trains_impacted'].sum()
    total_occurrences = delay_data['occurrences'].sum()

    # Overview metrics
    st.header("📊 Delay Impact Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Trains Impacted",
            f"{int(total_impact):,}",
            help="Total estimated trains affected by delays"
        )

    with col2:
        st.metric(
            "Delay Records",
            f"{int(total_occurrences):,}",
            help="Number of delay cause records analyzed"
        )

    with col3:
        top_cause = delay_data.iloc[0]['delay_cause_category']
        top_pct = (delay_data.iloc[0]['total_trains_impacted'] / total_impact * 100)
        st.metric(
            "Top Cause",
            top_cause,
            f"{top_pct:.1f}%",
            help="Most frequent delay cause"
        )

    with col4:
        years_str = ", ".join(map(str, sorted(selected_years)))
        st.metric(
            "Analysis Period",
            years_str,
            help="Years included in this analysis"
        )

    st.markdown("---")

    # Delay cause breakdown
    st.header("🎯 Delay Cause Breakdown")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Impact by Cause Category")

        # Sunburst chart
        fig = px.sunburst(
            delay_data,
            path=['delay_cause_category'],
            values='total_trains_impacted',
            title="Delay Causes (sized by trains impacted)",
            color='avg_cause_percentage',
            color_continuous_scale='RdYlGn_r',
            labels={'avg_cause_percentage': 'Avg %'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Causes")

        # Calculate percentages
        delay_data['impact_percentage'] = (delay_data['total_trains_impacted'] / total_impact * 100).round(2)

        for idx, row in delay_data.iterrows():
            st.markdown(f"""
            **{row['delay_cause_category']}**
            - {row['impact_percentage']}% of delays
            - {int(row['total_trains_impacted']):,} trains
            """)

    st.markdown("---")

    # Detailed comparison
    st.header("📊 Detailed Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trains Impacted by Cause")

        fig = px.bar(
            delay_data,
            x='delay_cause_category',
            y='total_trains_impacted',
            color='delay_cause_category',
            labels={
                'delay_cause_category': 'Cause Category',
                'total_trains_impacted': 'Trains Impacted'
            },
            title="Total Impact by Category"
        )
        fig.update_layout(
            template="plotly_white",
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Average Cause Percentage")

        fig = px.bar(
            delay_data,
            x='delay_cause_category',
            y='avg_cause_percentage',
            color='delay_cause_category',
            labels={
                'delay_cause_category': 'Cause Category',
                'avg_cause_percentage': 'Avg Percentage (%)'
            },
            title="Average Attribution to Each Cause"
        )
        fig.update_layout(
            template="plotly_white",
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Time series trend (if multiple years selected)
    if len(selected_years) > 1:
        st.header("📅 Trends Over Time")

        trends_query = f"""
        SELECT
            year,
            delay_cause_category,
            SUM(estimated_trains_delayed_by_cause) as total_impact
        FROM analytics_analytics.fct_tgv_delays_by_cause
        WHERE {where_clause}
        GROUP BY year, delay_cause_category
        ORDER BY year, total_impact DESC
        """

        trends_data = query_data(trends_query)

        if not trends_data.empty:
            fig = px.line(
                trends_data,
                x='year',
                y='total_impact',
                color='delay_cause_category',
                markers=True,
                labels={
                    'year': 'Year',
                    'total_impact': 'Trains Impacted',
                    'delay_cause_category': 'Cause'
                },
                title="Delay Cause Trends Over Time"
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Route-specific analysis (if route filter applied)
    if route_filter:
        st.header(f"🚄 Route Analysis: {route_filter}")

        route_detail_query = f"""
        SELECT
            route,
            delay_cause_category,
            SUM(estimated_trains_delayed_by_cause) as total_impact,
            AVG(cause_percentage) as avg_percentage
        FROM analytics_analytics.fct_tgv_delays_by_cause
        WHERE {where_clause}
        GROUP BY route, delay_cause_category
        ORDER BY total_impact DESC
        LIMIT 20
        """

        route_detail = query_data(route_detail_query)

        if not route_detail.empty:
            fig = px.bar(
                route_detail,
                x='route',
                y='total_impact',
                color='delay_cause_category',
                labels={
                    'route': 'Route',
                    'total_impact': 'Trains Impacted',
                    'delay_cause_category': 'Cause'
                },
                title=f"Top 20 Routes Affected by Delays (filtered by: {route_filter})"
            )
            fig.update_layout(template="plotly_white", xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Detailed data table
    st.header("📋 Detailed Delay Cause Data")

    st.dataframe(
        delay_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "delay_cause_category": "Cause Category",
            "cause_description": "Description",
            "occurrences": st.column_config.NumberColumn(
                "Occurrences",
                format="%d"
            ),
            "total_trains_impacted": st.column_config.NumberColumn(
                "Trains Impacted",
                format="%.0f"
            ),
            "avg_cause_percentage": st.column_config.NumberColumn(
                "Avg Attribution",
                format="%.2f%%"
            ),
            "impact_percentage": st.column_config.NumberColumn(
                "% of Total Impact",
                format="%.2f%%"
            ),
        }
    )

    # Download option
    csv = delay_data.to_csv(index=False)
    st.download_button(
        label="📥 Download Delay Analysis (CSV)",
        data=csv,
        file_name=f"sncf_delay_analysis_{'-'.join(map(str, selected_years))}.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # Insights section
    st.header("💡 Key Insights")

    st.markdown(f"""
    Based on the analysis of **{int(total_impact):,} delayed trains** across selected periods:

    1. **Primary Delay Cause:** {delay_data.iloc[0]['delay_cause_category']} accounts for {delay_data.iloc[0]['impact_percentage']:.1f}% of delays
    2. **Description:** {delay_data.iloc[0]['cause_description']}
    3. **Operational Focus:** The top 3 causes represent {delay_data.head(3)['impact_percentage'].sum():.1f}% of all delays

    **Recommendations:**
    - Focus operational improvements on the top 2-3 delay causes
    - Monitor trends over time to measure improvement initiatives
    - Route-specific analysis can identify localized issues
    """)

    # Footer
    st.markdown("---")
    render_footer()


if __name__ == "__main__":
    main()
