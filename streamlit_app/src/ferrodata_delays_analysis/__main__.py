"""
Point d'entrée principal de l'application ferrodata.
"""

import streamlit as st

from .components.sidebar import render_sidebar


def configure_page():
    """Configure la page principale de l'application."""
    st.set_page_config(
        page_title="ferrodata",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": """
            # ferrodata
            Interactive dashboard for analysing the performance of the french railway plateform.
            Developped by Slimane Lakehal
            """
        },
    )


def main():
    """Point d'entrée principal de l'application."""
    configure_page()

    # Titre principal
    st.title("🚀 ferrodata")
    st.markdown(
        "*Interactive dashboard for analysing the performance of the french railway plateform.*"
    )

    # Sidebar
    render_sidebar()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Développé avec ❤️ par Slimane Lakehal | "
        "<a href='mailto:lakehalslimane@gmail.com'>Contact</a>"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
