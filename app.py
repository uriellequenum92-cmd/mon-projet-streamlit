import streamlit as st
import pandas as pd
import plotly.express as px

def local_css():
    st.markdown("""
        <style>
        /* --- 1. POLICE GLOBALE (CORRIGÉE) --- */
        /* On cible le texte, mais ON EXCLUT les icônes (Material Icons) */
        html, body, p, h1, h2, h3, h4, h5, h6, span, div, label {
            font-family: 'Source Sans Pro', sans-serif;
        }
        
        /* Force les icônes Streamlit à garder leur police d'origine */
        button[kind="header"] > span {
            font-family: "Source Sans Pro", sans-serif !important; /* Fallback */
        }
        
        /* Si le bug persiste, on cache le texte de l'icône spécifiquement */
        div[data-testid="stSidebarCollapseButton"] span {
            display: none !important; /* Cache le texte bugué */
        }
        div[data-testid="stSidebarCollapseButton"]::before {
            content: "«"; /* Remplace par un simple guillemet si besoin */
            font-size: 20px;
            color: #A78BFA;
            font-weight: bold;
        }

        /* --- 2. LE TITRE (LABEL) EN VEDETTE --- */
        div[data-testid="stMetricLabel"] {
            font-size: 16px !important;
            font-weight: 900 !important;
            color: #A78BFA !important;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 5px !important;
        }

        /* --- 3. LA VALEUR (LE CHIFFRE) --- */
        div[data-testid="stMetricValue"] {
            font-size: 24px !important;
            font-weight: 400 !important;
            color: #E2E8F0 !important;
        }
        
        /* --- 4. TITRES SUR UNE LIGNE --- */
        h1, h2, h3 {
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

# N'oubliez pas d'appeler la fonction tout de suite après !
local_css()

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Dashboard Animes",
    page_icon="🎌",
    layout="wide"
)

# --- 1. CHARGEMENT ET NETTOYAGE DES DONNÉES (Mis en cache) ---
@st.cache_data
def load_and_clean_data():
    # Chargement
    try:
        df = pd.read_csv("animes.csv")
    except FileNotFoundError:
        st.error("Le fichier 'animes.csv' est introuvable. Veuillez le placer dans le même dossier.")
        return pd.DataFrame()

    # Nettoyage des colonnes
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Suppression doublons
    df = df.drop_duplicates(subset="anime")
    
    # Nettoyage texte
    text_cols = ["anime", "genre_tags", "source", "status", "studio"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df["anime"] = df["anime"].str.upper()
    
    # Conversion dates et notes
    df["date_pub"] = pd.to_datetime(df["date_pub"], errors="coerce")
    cols_notes = ["note_globale", "note_meilleur_ep", "note_pire_ep"]
    for col in cols_notes:
        if col in df.columns:
            df[col] = df[col].clip(0, 10)

    # Gestion des genres (extraction du principal)
    df["genre_tags"] = df["genre_tags"].str.lower().str.replace(" ", "").str.split("/")
    df["genre_principal"] = df["genre_tags"].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else "Inconnu")
    
    return df

# Chargement des données
df = load_and_clean_data()

if df.empty:
    st.stop()

# --- 2. BARRE LATÉRALE (FILTRES) ---
# --- 2. BARRE LATÉRALE (FILTRES COMPLETS) ---
# --- 2. BARRE LATÉRALE (FILTRES COMPLETS) ---
with st.sidebar:
    # A. Le Titre principal de l'app
    st.title("⛩️ Anime Viz")
    
    # B. Votre En-tête "Filtres" avec l'icône (Votre code)
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px; border-bottom: 1px solid #334155; padding-bottom: 10px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
            </svg>
            <span style="font-size: 1.1rem; font-weight: 600; color: #F8FAFC;">Filtres</span>
        </div>
    """, unsafe_allow_html=True)

    # C. Les Widgets (Les boutons de contrôle)
    # 1. Studio
    all_studios = sorted(df["studio"].unique())
    selected_studio = st.multiselect("Sélectionner un Studio", all_studios, default=all_studios[:5])

    # 2. Genre
    all_genres = sorted(df["genre_principal"].unique())
    selected_genre = st.multiselect("Sélectionner un Genre", all_genres, default=all_genres)

    # 3. Statut
    all_status = df["status"].unique()
    selected_status = st.multiselect("Statut", all_status, default=all_status)

    # 4. Note (Slider)
    min_note = st.slider("Note minimale", 0.0, 10.0, 7.0, step=0.1)

# --- IMPORTANT : APPLICATION DU FILTRE (Juste après la sidebar) ---
# Sans ce bloc, vous aurez l'erreur "df_filtre is not defined"
df_filtre = df[
    (df["studio"].isin(selected_studio) if selected_studio else True) &
    (df["genre_principal"].isin(selected_genre) if selected_genre else True) &
    (df["status"].isin(selected_status) if selected_status else True) &
    (df["note_globale"] >= min_note)
]

# --- 3. DASHBOARD PRINCIPAL ---
st.title("🎌 Analyse Interactive des Animés")
st.markdown(f"**{len(df_filtre)}** animés correspondent à vos critères.")

# KPIs (Indicateurs Clés)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Note Moyenne", f"{df_filtre['note_globale'].mean():.2f}/10")
with col2:
    try:
        top_anime = df_filtre.loc[df_filtre['note_globale'].idxmax()]['anime']
    except:
        top_anime = "N/A"
    st.metric("Top Animé", top_anime)
with col3:
    st.metric("Total Épisodes", f"{df_filtre['nb_episodes'].sum():,.0f}")
with col4:
    st.metric("Studio dominant", df_filtre['studio'].mode()[0] if not df_filtre.empty else "N/A")

st.divider()

# --- 4. GRAPHIQUES INTERACTIFS ---

# Onglets pour organiser la vue
tab1, tab2, tab3 = st.tabs(["📊 Distribution & Notes", "🏢 Studios & Statuts", "💾 Données Brutes"])

with tab1:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Distribution des Notes")
        
        fig_hist = px.histogram(
            df_filtre, 
            x="note_globale", 
            nbins=20, 
            title="Répartition des notes globales",
            color_discrete_sequence=["#A78BFA"], # Violet "Lilas" assorti au thème
            text_auto=True,
            template="plotly_dark" # <--- Thème sombre
        )
        
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Note",
            yaxis_title="Nombre d'animés"
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with col_g2:
        st.subheader("Note vs Nombre d'épisodes")
        
        # Création du graphique avec le template sombre
        fig_scatter = px.scatter(
            df_filtre, 
            x="nb_episodes", 
            y="note_globale", 
            size="note_globale", 
            color="genre_principal",
            hover_name="anime",
            title="Y a-t-il un lien entre durée et qualité ?",
            log_x=True,
            template="plotly_dark"  # <--- Ajout du thème sombre
        )

        # Application de la transparence pour le fond
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", # Fond du cadre transparent
            plot_bgcolor="rgba(0,0,0,0)",  # Fond du graphique transparent
            font=dict(color="white")       # Texte en blanc
        )

        # Affichage
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    col_s1, col_s2 = st.columns(2)
    
    # --- GRAPHIQUE CAMEMBERT (PIE CHART) ---
    with col_s1:
        st.subheader("Répartition par Statut")
        statut_counts = df_filtre["status"].value_counts().reset_index()
        statut_counts.columns = ["status", "count"]
        
        fig_pie = px.pie(
            statut_counts, 
            values="count", 
            names="status", 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu,
            template="plotly_dark" # <--- Thème sombre
        )
        
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
    # --- GRAPHIQUE EN BARRES (BAR CHART) ---
    with col_s2:
        st.subheader("Top Studios (Volume)")
        studio_counts = df_filtre["studio"].value_counts().head(10).reset_index()
        studio_counts.columns = ["studio", "count"]
        
        fig_bar = px.bar(
            studio_counts, 
            x="count", 
            y="studio", 
            orientation='h',
            text_auto=True,
            color="count",
            color_continuous_scale="Viridis",
            template="plotly_dark" # <--- Thème sombre
        )
        
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            yaxis=dict(autorange="reversed") # Pour avoir le Top 1 en haut
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
with tab3:
    st.subheader("Explorateur de données")
    st.dataframe(df_filtre.sort_values(by="note_globale", ascending=False))
    
    # Bouton de téléchargement
    csv = df_filtre.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Télécharger les données filtrées (CSV)",
        data=csv,
        file_name="animes_filtrés.csv",
        mime="text/csv",
    )

    # --- 5. SECTION FICHE DÉTAILLÉE (ENCYCLOPÉDIE) ---
st.divider() # Ligne de séparation
st.header("📚 Encyclopédie des Animés")

# 1. Le Menu Déroulant (Trié par ordre alphabétique)
liste_animes_triee = sorted(df["anime"].unique())
choix_anime = st.selectbox("Sélectionnez un animé pour voir sa fiche complète :", liste_animes_triee)

# 2. Récupération des données de la ligne sélectionnée
# on prend la première ligne trouvée (.iloc[0])
anime_data = df[df["anime"] == choix_anime].iloc[0]

# 3. Mise en page : Image à gauche (1/3), Infos à droite (2/3)
col_img, col_info = st.columns([1, 2], gap="large")

with col_img:
    # Gestion de l'image (si le lien existe)
    if "image_url" in df.columns and pd.notna(anime_data["image_url"]) and anime_data["image_url"] != "":
        st.image(
            anime_data["image_url"], 
            caption=f"Affiche de {anime_data['anime']}", 
            use_container_width=True
        )
    else:
        # Image de remplacement stylée si pas d'image
        st.info("🖼️ Image non disponible")
        st.markdown(
            """
            <div style="background-color: #334155; height: 300px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                <span style="color: #94A3B8;">No Image</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
with col_info:
    # 1. LE TITRE CENTRÉ
    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            justify-content: center; /* <--- C'est ici que ça se joue ! */
            gap: 10px; 
            margin-bottom: 15px;
        ">
            <span style="font-size: 30px;">🎌</span>
            <span style="
                font-size: 26px; 
                font-weight: 900; 
                color: #FFFFFF; 
                white-space: nowrap; 
                overflow: hidden; 
                text-overflow: ellipsis;
            ">
                {anime_data['anime']}
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. LES TAGS (GENRES) CENTRÉS
    if "genre_tags" in df.columns:
        tags = anime_data["genre_tags"]
        if isinstance(tags, list):
            # On prépare le HTML des tags
            html_tags_content = ""
            for tag in tags:
                html_tags_content += f"""
                <span style="
                    display: inline-block;
                    background-color: rgba(167, 139, 250, 0.2);
                    color: #A78BFA;
                    padding: 5px 12px;
                    border-radius: 15px;
                    font-size: 12px;
                    font-weight: 700;
                    margin: 0 3px 5px 3px; /* Espacement ajusté */
                ">{tag.strip()}</span>"""
            
            # On enveloppe le tout dans une div centrée
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 20px;">
                    {html_tags_content}
                </div>
            """, unsafe_allow_html=True)

    # ... (La suite avec kpi_html reste identique)

    # 3. LA LIGNE DES CHIFFRES (KPIs) - STYLE FORCÉ
    # On crée 3 colonnes Streamlit
    k1, k2, k3 = st.columns(3)

    # Fonction pour générer le HTML forcé
    def kpi_html(titre, valeur, couleur_valeur="#FFFFFF"):
        return f"""
        <div style="text-align: center;">
            <div style="
                color: #A78BFA !important;
                font-size: 14px !important;
                font-weight: 900 !important;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 5px;
            ">
                {titre}
            </div>
            <div style="
                color: {couleur_valeur} !important;
                font-size: 22px !important;
                font-weight: 400 !important;
            ">
                {valeur}
            </div>
        </div>
        """

    with k1:
        studio = anime_data.get("studio", "N/A")
        st.markdown(kpi_html("Studio", studio), unsafe_allow_html=True)

    with k2:
        note = anime_data.get("note_globale", 0)
        # Vert si top, Blanc sinon
        couleur = "#4ade80" if note >= 8.5 else "#FFFFFF" 
        st.markdown(kpi_html("Note", f"{note}/10", couleur), unsafe_allow_html=True)

    with k3:
        eps = anime_data.get("nb_episodes", "?")
        st.markdown(kpi_html("Épisodes", f"{eps} eps"), unsafe_allow_html=True)

    st.markdown("---")

    # 4. DESCRIPTION
    st.markdown("### 📝 L'Analyse")
    desc = anime_data.get("comm_saison_1", "Pas de description.")
    
    # Boite de description stylisée
    st.markdown(f"""
        <div style="
            background-color: #1E293B;
            border-left: 5px solid #A78BFA;
            padding: 15px;
            border-radius: 5px;
            color: #E2E8F0;
            font-size: 16px;
            line-height: 1.5;
        ">
            {desc}
        </div>
    """, unsafe_allow_html=True)

    # Bonus : Afficher le meilleur épisode
    if "meilleur_ep_titre" in df.columns:
        best_ep = anime_data["meilleur_ep_titre"]
        note_best = anime_data.get("note_meilleur_ep", "?")
        st.success(f"💎 **À ne pas rater :** {best_ep} (Note: {note_best})")