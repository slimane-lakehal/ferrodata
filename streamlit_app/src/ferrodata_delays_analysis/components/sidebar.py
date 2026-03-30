"""
Composant Sidebar - Navigation et informations latérales
"""

from datetime import date

import streamlit as st


def render_sidebar():
    """Affiche la sidebar avec navigation et informations."""

    with st.sidebar:
        st.header("🔍 Filters")
        st.markdown("---")

        # Date range filter
        default_start = "2013-01-01"
        default_end = date.today()

        date_range = st.date_input(
            "Date Range",
            value=(default_start, default_end),
            help="Select the time period for analysis",
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
            help="Select which train services to include",
        )

        st.markdown("---")
        st.info("💡 Use the navigation above to explore detailed analytics")
    return start_date, end_date, service_types

def render_mini_sidebar():
    """Version minimaliste de la sidebar pour les pages spécifiques."""
    with st.sidebar:
        st.markdown("### 🚀 ferrodata")
        st.markdown("---")

        # Retour à l'accueil
        if st.button("🏠 Retour à l'accueil"):
            st.switch_page("main.py")

        # Informations essentielles
        st.markdown("👤 Slimane Lakehal")
        st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")


if __name__ == "__main__":
    # Test du composant
    st.set_page_config(page_title="Test Sidebar", layout="wide")
    st.title("Test du composant Sidebar")
    render_sidebar()
    st.write("Contenu principal de la page...")
