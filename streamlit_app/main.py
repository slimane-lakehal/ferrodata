#!/usr/bin/env python3
"""
Ferrodata - SNCF Train Punctuality Analytics
Interactive dashboard for analyzing French railway performance.

Author: Slimane Lakehal <lakehalslimane@gmail.com>
Template: Based on Gaël Penessot's modern Streamlit template
         (https://github.com/gpenessot)
"""

import sys
from pathlib import Path

# Add src folder to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="SNCF Analytics - Ferrodata",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="auto"
)

# Define pages with top navigation
pages = [
    st.Page(
        "src/ferrodata_delays_analysis/pages/1_home.py",
        title="Home",
        icon=":material/home:",
        default=True
    ),
    st.Page(
        "src/ferrodata_delays_analysis/pages/4_station_map.py",
        title="Station Map",
        icon=":material/map:"
    ),
    st.Page(
        "src/ferrodata_delays_analysis/pages/5_route_explorer.py",
        title="Route Explorer",
        icon=":material/route:"
    ),
    st.Page(
        "src/ferrodata_delays_analysis/pages/6_delay_analysis.py",
        title="Delay Analysis",
        icon=":material/analytics:"
    ),
    st.Page(
        "src/ferrodata_delays_analysis/pages/3_settings.py",
        title="Settings",
        icon=":material/settings:"
    ),
]

# Navigation at top position
page = st.navigation(pages, position="top")

# Execute the page
page.run()