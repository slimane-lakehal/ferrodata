"""
Footer Component - Page footer with credits and information
"""

import streamlit as st
from datetime import datetime


def render_footer():
    """Display footer with credits and information."""

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("🚄 **Ferrodata** | SNCF Analytics v1.0")

    with col2:
        st.caption("💻 Built by **Slimane Lakehal** | Template by [Gaël Penessot](https://github.com/gpenessot)")

    with col3:
        st.caption(f"📅 Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
