import streamlit as st
import mysql.connector
import os
import pandas as pd
from dotenv import load_dotenv

# Configuration MySQL
_MYSQL_ROOT_PASSWORD="mysql"
_MYSQL_DATABASE="TYROK"
_MYSQL_USER="nanp"
_MYSQL_PASSWORD="nanp"
# Configuration App (utilisée par Streamlit)
_DB_HOST="mysql"
_DB_PORT=3306
# nom de l'application
_APP_NAME="Gestion Pro Clients"

# Charge les variables du fichier .env situé dans le même dossier
load_dotenv()

# Configuration MySQL
MYSQL_ROOT_PASSWORD=os.getenv("MYSQL_ROOT_PASSWORD", _MYSQL_ROOT_PASSWORD)
MYSQL_DATABASE=os.getenv("MYSQL_DATABASE", _MYSQL_DATABASE)
MYSQL_USER=os.getenv("MYSQL_USER", _MYSQL_USER)
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD", _MYSQL_PASSWORD)
# Configuration App (utilisée par Streamlit)
DB_HOST=os.getenv("DB_HOST", _DB_HOST)
DB_PORT=os.getenv("DB_PORT", _DB_PORT)
# nom de l'application
APP_NAME=os.getenv("APP_NAME", _APP_NAME)

# Connexion via variables d'env (chargées par Docker)
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    
#print(f"db host: {os.getenv('DB_HOST')}")
#print(f"db port: {os.getenv('DB_PORT')}")
#print(f"db user: {os.getenv('MYSQL_USER')}")
#print(f"db name: {os.getenv('MYSQL_DATABASE')}")

st.set_page_config(
    page_title=f"{APP_NAME}",
    page_icon="💼",
    layout="wide", # Mode large pour plus de confort
    initial_sidebar_state="expanded"    
)

# --- FANCY CSS ---
st.markdown("""
    <style>
    /* Style global et fond */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Carte pour le formulaire */
    div[data-testid="stForm"] {
        border: none;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        background-color: white;
        padding: 2rem;
    }
    
    /* Style des titres */
    h1 {
        color: #1E3A8A;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Style du bouton de soumission */
    button[kind="primaryFormSubmit"] {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px !important;
        width: 100%;
        border: none;
        transition: 0.3s;
    }
    
    button[kind="primaryFormSubmit"]:hover {
        background-color: #1D4ED8 !important;
        transform: translateY(-2px);
    }

    /* Badge "Actif" */
    .status-active {
        color: #059669;
        font-weight: bold;
        background-color: #D1FAE5;
        padding: 2px 8px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    

st.title(f"🚀 {APP_NAME}")

col1, col2 = st.columns([1, 2], gap="large")

# --- Interface d'ajout ---
with col1:
    st.subheader("➕ Nouveau Client")
    with st.form("add_client_form"):
        code = st.text_input("Code unique", placeholder="ex: C001")
        name = st.text_input("Nom du client", placeholder="ex: John Doe")
        actif = st.toggle("Client Actif", value=True)
        
        if st.form_submit_button("Enregistrer"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO client (code, name, actif) VALUES (%s, %s, %s)",
                    (code, name, actif)
                )
                conn.commit()                
                st.toast(f"Client {name} ajouté !", icon="✅")
                conn.close()
            except Exception as e:
                st.error(f"Erreur : {e}")

# --- Interface de consultation ---
with col2:
    st.subheader("📋 Liste des clients")
    try:
        conn = get_connection()
        query = "SELECT id, code, name, actif FROM client ORDER BY id DESC"
        # Utilisation du cache Streamlit pour la lecture        
        df = pd.read_sql(query, conn)
        st.dataframe(
            df,
            column_config={
                "id": None, # Masquer l'ID
                "code": st.column_config.TextColumn("Code"),
                "name": st.column_config.TextColumn("Nom Client"),
                "actif": st.column_config.CheckboxColumn("Statut")                
            },
            use_container_width=True,
            hide_index=True
        )
        conn.close()
    except Exception as e:
        st.info("La base de données est en cours de démarrage ou vide.")
        st.error(f"Erreur : {e}")