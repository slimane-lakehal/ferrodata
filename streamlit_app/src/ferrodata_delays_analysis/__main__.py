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
            'About': """
            # ferrodata
            Interactive dashboard for analysing the performance of the french railway plateform.
            
            Developped by Slimane Lakehal
            """
        }
    )


def main():
    """Point d'entrée principal de l'application."""
    configure_page()

    # Titre principal
    st.title("🚀 ferrodata")
    st.markdown("*Interactive dashboard for analysing the performance of the french railway plateform.*")

    # Sidebar
    render_sidebar()

    # Contenu principal
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("---")

        # Message de bienvenue
        st.markdown("""
        ## 👋 Bienvenue !
        
        Cette application démo vous montre les bonnes pratiques pour structurer 
        vos projets Streamlit de façon professionnelle.
        
        ### 🎯 Fonctionnalités de ce template :
        - ✅ Structure modulaire et organisée
        - ✅ Pages multiples avec navigation
        - ✅ Composants réutilisables
        - ✅ Configuration optimisée
        - ✅ Données d'exemple intégrées
        
        ### 🧭 Navigation
        Utilisez la **sidebar** à gauche pour naviguer entre les différentes pages.
        """)

        # Call-to-action subtil pour la formation
        with st.expander("🎓 Envie d'aller plus loin ?"):
            st.markdown("""
            Ce template démo vous donne un aperçu des possibilités.
            
            **Dans notre formation complète, vous apprendrez :**
            - Tests automatisés et CI/CD
            - Déploiement en production
            - Gestion avancée des états
            - Authentification utilisateur
            - Intégration base de données
            - Monitoring et analytics
            
            👉 [**Découvrir la formation**](https://votre-lien-formation.com)
            """)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Développé avec ❤️ par Slimane Lakehal | "
        "<a href='mailto:lakehalslimane@gmail.com'>Contact</a>"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
