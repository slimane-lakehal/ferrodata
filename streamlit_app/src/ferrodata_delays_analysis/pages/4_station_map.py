"""
🗺️ Interactive Station Map

Visualize all SNCF stations on an interactive map with performance metrics.
"""

import numpy as np
import pydeck as pdk
import streamlit as st

from ferrodata_delays_analysis.components.footer import render_footer
from ferrodata_delays_analysis.utils.database import query_data, MART_SCHEMA


def main():
    """Interactive station map page."""

    st.title("🗺️ Interactive Station Map")
    st.markdown("""
    Explore all passenger train stations across France. Stations are color-coded by tier
    and sized by total train volume.
    """)

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Map Filters")
        st.markdown("---")

        # Station tier filter
        tier_options = ["Major Hub", "Regional Hub", "Medium Station", "Small Station", "Inactive/Freight Only"]
        selected_tiers = st.multiselect(
            "Station Tier",
            options=tier_options,
            default=["Major Hub", "Regional Hub", "Medium Station"],
            help="Filter stations by size/importance"
        )

        # Minimum traffic filter
        min_trains = st.slider(
            "Minimum Trains Handled",
            min_value=0,
            max_value=100000,
            value=0,
            step=1000,
            help="Show only stations with at least this many trains"
        )

        st.markdown("---")

        # Color legend
        st.markdown("### 🎨 Color Legend")
        st.markdown("""
        - 🔴 **Red**: Major Hub
        - 🟠 **Orange**: Regional Hub
        - 🟡 **Yellow**: Medium Station
        - 🟢 **Green**: Small Station
        - ⚫ **Gray**: Inactive/Freight Only
        """)

    # Fetch station data
    query = f"""
    SELECT
        station_id,
        station_name,
        city,
        department,
        longitude,
        latitude,
        station_tier,
        total_trains_handled,
        has_passenger_service,
        has_freight_service
    FROM {MART_SCHEMA}.dim_stations
    WHERE longitude IS NOT NULL
        AND latitude IS NOT NULL
        AND station_tier IN ({','.join([f"'{t}'" for t in selected_tiers])})
        AND total_trains_handled >= {min_trains}
    ORDER BY total_trains_handled DESC
    """

    stations = query_data(query)

    if stations.empty:
        st.warning("⚠️ No stations match your filter criteria. Try adjusting the filters.")
        st.stop()


    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Stations Shown", f"{len(stations):,}")
    with col2:
        st.metric("🚂 Total Trains", f"{stations['total_trains_handled'].sum():,.0f}")
    with col3:
        avg_trains = stations['total_trains_handled'].mean()
        st.metric("📊 Avg Trains per Station", f"{avg_trains:,.0f}")

    st.markdown("---")

    # Color mapping
    tier_colors = {
        'Major Hub': [255, 0, 0, 180],
        'Regional Hub': [255, 165, 0, 180],
        'Medium Station': [255, 255, 0, 180],
        'Small Station': [0, 255, 0, 180],
        'Inactive/Freight Only': [128, 128, 128, 180]
    }

    stations['color'] = stations['station_tier'].map(tier_colors)

    # Scale marker size (logarithmic for better visualization)
    stations['marker_size'] = np.log1p(stations['total_trains_handled']) * 50

    # Ensure coordinates are proper floats
    stations['longitude'] = stations['longitude'].astype(float)
    stations['latitude'] = stations['latitude'].astype(float)

    # Create PyDeck map
    st.subheader("📍 Station Locations")

    # Try-except to catch any rendering issues
    try:
        view_state = pdk.ViewState(
            latitude=46.5,
            longitude=2.5,
            zoom=5,
            pitch=0,
        )

        layer = pdk.Layer(
            'ScatterplotLayer',
            data=stations,
            get_position='[longitude, latitude]',
            get_fill_color='color',
            get_radius='marker_size',
            pickable=True,
            auto_highlight=True,
            opacity=0.8,
            radius_min_pixels=3,
            radius_max_pixels=50,
        )

        tooltip = {
            'html': '''
                <b>{station_name}</b><br/>
                <i>{city}, {department}</i><br/>
                <hr style="margin: 5px 0;">
                Tier: {station_tier}<br/>
                Trains Handled: {total_trains_handled}<br/>
                Passenger Service: {has_passenger_service}<br/>
                Freight Service: {has_freight_service}
            ''',
            'style': {
                'backgroundColor': 'steelblue',
                'color': 'white',
                'padding': '10px',
                'borderRadius': '5px'
            }
        }

        st.pydeck_chart(pdk.Deck(
            map_style='https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip
        ))

    except Exception as e:
        st.error(f"⚠️ Map rendering error: {e}")
        st.info("💡 Fallback: Using simple map view")

        # Fallback to built-in Streamlit map
        st.map(
            data=stations,
            latitude='latitude',
            longitude='longitude',
            size='marker_size',
            color='color'
        )

    st.markdown("---")

    # Station details table
    st.subheader("📋 Station Details")

    # Select specific stations
    search_term = st.text_input(
        "🔍 Search Stations",
        placeholder="Enter station name, city, or department...",
        help="Filter the table below"
    )

    if search_term:
        filtered_stations = stations[
            stations['station_name'].str.contains(search_term, case=False, na=False) |
            stations['city'].str.contains(search_term, case=False, na=False) |
            stations['department'].str.contains(search_term, case=False, na=False)
        ]
    else:
        filtered_stations = stations

    # Display table
    st.dataframe(
        filtered_stations[[
            'station_name', 'city', 'department', 'station_tier',
            'total_trains_handled', 'has_passenger_service', 'has_freight_service'
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "station_name": "Station",
            "city": "City",
            "department": "Department",
            "station_tier": "Tier",
            "total_trains_handled": st.column_config.NumberColumn(
                "Trains Handled",
                format="%d"
            ),
            "has_passenger_service": st.column_config.CheckboxColumn(
                "Passenger",
                help="Has passenger service"
            ),
            "has_freight_service": st.column_config.CheckboxColumn(
                "Freight",
                help="Has freight service"
            ),
        }
    )

    # Download option
    csv = filtered_stations.to_csv(index=False)
    st.download_button(
        label="📥 Download Station Data (CSV)",
        data=csv,
        file_name="sncf_stations.csv",
        mime="text/csv"
    )

    # Footer
    st.markdown("---")
    render_footer()


if __name__ == "__main__":
    main()
