#!/usr/bin/env python3
"""
Ferrodata - SNCF Train Punctuality Analytics
Interactive dashboard for analyzing French railway performance.

Author: Slimane Lakehal <lakehalslimane@gmail.com>
Template: Based on Gaël Penessot's modern Streamlit template
         (https://www.mes-formations-data.fr/streamlit-turbo)
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
        "src/ferrodata_delays_analysis/pages/home.py",
        title="Home",
        icon=":material/home:",
        default=True
    ),
    st.Page(
        "src/ferrodata_delays_analysis/pages/station_map.py",
        title="Station Map",
        icon=":material/map:"
    ),
    st.Page(
        "src/ferrodata_delays_analysis/pages/route_explorer.py",
        title="Route Explorer",
        icon=":material/route:"
    ),
    st.Page(
        "src/ferrodata_delays_analysis/pages/delay_analysis.py",
        title="Delay Analysis",
        icon=":material/analytics:"
    )
]

# Navigation at top position
page = st.navigation(pages, position="top")

# Execute the page
page.run()