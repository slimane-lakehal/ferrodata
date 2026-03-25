"""
Composant Sidebar - Navigation et informations latérales
"""

import streamlit as st
from datetime import datetime


def render_sidebar():
    """Affiche la sidebar avec navigation et informations."""
    
    with st.sidebar:
        # Logo/Header de l'application
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='margin: 0; color: #FF6B6B;'>🚀</h1>
            <h3 style='margin: 0.5rem 0 0 0;'>ferrodata</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation principale
        st.markdown("### 🧭 Navigation")
        st.markdown("""
        Utilisez le menu de pages de Streamlit pour naviguer :
        - 🏠 **Accueil** : Page principale
        - 📊 **Dashboard** : Visualisations et analytics  
        - ⚙️ **Settings** : Configuration de l'app
        """)
        
        st.markdown("---")
        
        # Informations sur la session
        st.markdown("### 📊 Session info")
        
        # Informations utilisateur
        if 'user_name' in st.session_state:
            st.markdown(f"👤 **Utilisateur :** {st.session_state.user_name}")
        else:
            st.markdown("👤 **Utilisateur :** Slimane Lakehal")
        
        # Heure de connexion simulée
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
        
        session_duration = datetime.now() - st.session_state.session_start
        minutes = int(session_duration.total_seconds() // 60)
        seconds = int(session_duration.total_seconds() % 60)
        
        st.markdown(f"⏱️ **Session :** {minutes}m {seconds}s")
        st.markdown(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
        st.markdown(f"🕐 **Heure :** {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Statistiques rapides
        st.markdown("### 📈 Aperçu rapide")
        
        # Métriques simulées
        st.metric(
            label="📊 Pages vues",
            value="1,234",
            delta="12%"
        )
        
        st.metric(
            label="👥 Utilisateurs actifs",
            value="56",
            delta="-3%"
        )
        
        st.metric(
            label="⚡ Performance",
            value="98%",
            delta="2%"
        )
        
        st.markdown("---")
        
        # Actions rapides
        st.markdown("### ⚡ Actions rapides")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄", help="Actualiser les données"):
                st.rerun()
        
        with col2:
            if st.button("📥", help="Exporter les données"):
                st.success("Export démarré !")
        
        # Bouton de déconnexion simulé
        if st.button("🚪 Déconnexion", type="secondary", use_container_width=True):
            # Réinitialiser la session
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Déconnexion réussie !")
            st.rerun()
        
        st.markdown("---")
        
        # Section d'aide
        with st.expander("❓ Aide & Support"):
            st.markdown("""
            **🆘 Besoin d'aide ?**
            
            - 📚 Consultez la documentation
            - 💬 Contactez le support : lakehalslimane@gmail.com
            - 🐛 Signaler un bug
            - 💡 Suggérer une amélioration
            
            **🎓 Formation complète**
            
            Ce template démo vous plaît ? 
            Découvrez la version complète avec :
            - Tests automatisés
            - Déploiement cloud
            - Base de données
            - Authentification
            - Et bien plus !
            
            👉 [En savoir plus](https://votre-lien-formation.com)
            """)
        
        # Footer de la sidebar
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; font-size: 0.8em; color: gray;'>"
            f"v1.0.0 | Développé avec ❤️<br>"
            f"par Slimane Lakehal"
            "</div>", 
            unsafe_allow_html=True
        )


def render_mini_sidebar():
    """Version minimaliste de la sidebar pour les pages spécifiques."""
    with st.sidebar:
        st.markdown("### 🚀 ferrodata")
        st.markdown("---")
        
        # Retour à l'accueil
        if st.button("🏠 Retour à l'accueil"):
            st.switch_page("main.py")
        
        # Informations essentielles
        st.markdown(f"👤 Slimane Lakehal")
        st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")


if __name__ == "__main__":
    # Test du composant
    st.set_page_config(page_title="Test Sidebar", layout="wide")
    st.title("Test du composant Sidebar")
    render_sidebar()
    st.write("Contenu principal de la page...")