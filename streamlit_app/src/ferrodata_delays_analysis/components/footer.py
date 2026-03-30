"""
Footer Component - Page footer with credits and information
"""

from datetime import datetime

import streamlit as st


def render_footer():
    """Display footer with credits and information."""

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("🚄 **Ferrodata** | SNCF Analytics v1.0")

    with col2:
        st.caption(
            "💻 Built by **Slimane Lakehal** | Template by [Gaël Penessot](https://www.mes-formations-data.fr/streamlit-turbo)"
        )

    with col3:
        st.caption(f"📅 Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
