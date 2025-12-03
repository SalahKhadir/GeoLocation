import streamlit as st
import pandas as pd
from pymongo import MongoClient

# ==========================================
# 1. CONFIGURATION & CONNEXION
# ==========================================
st.set_page_config(page_title="Travel & Food Hunter", page_icon="✈️", layout="wide")

# Fonction pour se connecter (avec cache pour la performance)
@st.cache_resource
def get_database():
    # Remplace par ton lien de connexion si besoin
    client = MongoClient("mongodb://localhost:27017/")
    return client.geoloca  # Nom de ta base de données

db = get_database()

# ==========================================
# 2. INTERFACE UTILISATEUR (SIDEBAR)
# ==========================================
st.sidebar.header("🔍 Filtres de recherche")

# ==========================================
# 3. CŒUR DE L'APPLICATION
# ==========================================
st.title("✈️ Airbnb & Food Hunter")
st.markdown("Trouvez un logement et découvrez les meilleurs restos autour grâce au **GeoSpatial Indexing**.")

selected_airbnb = None

# Option pour rechercher par nom personnalisé ou liste prédéfinie
search_option = st.radio("Mode de recherche:", ["Liste prédéfinie", "Recherche personnalisée"], horizontal=True)

if search_option == "Liste prédéfinie":
    # On propose une liste déroulante avec quelques apparts connus
    example_names = [
        "Private Room in Bushwick",
        "Ribeira Charming Duplex",
        "Horto flat with small garden",
        "Apt Linda Vista Lagoa - Rio",
        "Modern Spacious 1 Bedroom Loft",
        "Charming Flat in Downtown Moda",
        "Soho Cozy, Spacious and Convenient",
        "Nice room in Barcelona Center",
        "Deluxe Loft Suite",
        "Copacabana Apartment Posto 6"
    ]
    name_input = st.selectbox("Choisissez un logement:", example_names)
    selected_airbnb = db.listings.find_one({"name": name_input})
else:
    # Recherche personnalisée
    custom_name = st.text_input("Entrez le nom de l'appartement:")
    if custom_name:
        selected_airbnb = db.listings.find_one({"name": {"$regex": custom_name, "$options": "i"}})

# ==========================================
# 4. AFFICHAGE DES RÉSULTATS
# ==========================================
if selected_airbnb:
    # Colonne gauche (Infos), Colonne droite (Carte)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.success(f"Logement trouvé : {selected_airbnb['name']}")
        st.write(f"🏠 **Type:** {selected_airbnb.get('property_type', 'N/A')}")
        st.write(f"🛏️ **Chambres:** {selected_airbnb.get('bedrooms', 0)}")
        price = selected_airbnb.get('price', 'N/A')
        st.metric("Prix par nuit", f"{price}")
        
        # Récupération des coordonnées (GeoJSON)
        coords = selected_airbnb['address']['location']['coordinates']
        lon, lat = coords[0], coords[1] # Mongo est [Lon, Lat]

    with col2:
        # Affichage de la carte centrée sur l'appart avec marqueur personnalisé
        appart_data = pd.DataFrame({
            'lat': [lat], 
            'lon': [lon],
            'color': ['#FF0000'],  # Rouge vif pour l'appartement
            'size': [200]  # Plus grand que les restaurants
        })
        st.map(appart_data, latitude='lat', longitude='lon', color='color', size='size', zoom=14)

    # ==========================================
    # 5. LA REQUÊTE GEOSPATIALE ($NEAR)
    # ==========================================
    st.divider()
    st.subheader(f"🍔 Restaurants à moins de 1km de : {selected_airbnb['name']}")
    
    # Curseur pour choisir la distance (Interactivité = Points Bonus)
    distance_km = st.slider("Rayon de recherche (km)", 0.5, 5.0, 1.0)
    
    # Requête MongoDB GeoSpatial
    restos = list(db.restaurants.find({
        "address.coord": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "$maxDistance": distance_km * 1000 # Conversion en mètres
            }
        }
    }, {"name": 1, "cuisine": 1, "address.coord": 1, "grades": 1}).limit(10))

    if restos:
        # Palette de couleurs pour les restaurants
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                  '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788']
        
        # On prépare les données pour une belle carte avec TOUS les points
        map_restos = []
        sizes = []
        for idx, r in enumerate(restos):
            map_restos.append({
                'lat': r['address']['coord'][1],
                'lon': r['address']['coord'][0],
                'name': r['name'],
                'cuisine': r['cuisine'],
                'color': colors[idx % len(colors)],  # Rotation des couleurs
                'size': 100  # Taille normale pour restaurants
            })
        
        # On ajoute l'appart avec une couleur distinctive et plus petit
        map_restos.append({
            'lat': lat, 
            'lon': lon, 
            'name': '📍 YOU ARE HERE', 
            'cuisine': 'Votre Appartement',
            'color': '#FF0000',  # Rouge vif pour se démarquer
            'size': 50  # Plus petit que les restaurants
        })
        
        # Affichage en tableau propre avec couleurs
        df_restos = pd.DataFrame(restos)
        if not df_restos.empty:
            # Créer un DataFrame avec les couleurs pour l'affichage
            df_display = df_restos[['name', 'cuisine']].copy()
            
            # Afficher le tableau sans colonne de couleur
            st.table(df_display)
            
            # Légende des couleurs sous le tableau
            st.markdown("**Légende des couleurs sur la carte:**")
            cols = st.columns(5)
            color_names = ['Rouge', 'Turquoise', 'Bleu', 'Orange', 'Vert menthe', 
                          'Jaune', 'Violet', 'Bleu clair', 'Or', 'Vert']
            for i in range(min(len(restos), 10)):
                col_idx = i % 5
                with cols[col_idx]:
                    st.markdown(f'<div style="display:inline-block; width:15px; height:15px; background-color:{colors[i]}; border-radius:50%; margin-right:5px;"></div> {i+1}. {df_restos.iloc[i]["name"][:20]}...', unsafe_allow_html=True)
            
            # Carte avancée avec tous les points colorés
            df_map = pd.DataFrame(map_restos)
            st.map(df_map, latitude='lat', longitude='lon', color='color', size='size')
    else:
        st.warning("Aucun restaurant trouvé dans cette zone (Essayez d'augmenter le rayon !)")

elif not selected_airbnb:
    st.info("Sélectionnez un appartement pour voir les restaurants à proximité ✨")