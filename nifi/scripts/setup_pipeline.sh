#!/bin/bash

set -e # Arrête le script en cas d'erreur

# Configuration des URLs (Accès interne au réseau Docker)
CONNECT_URL="http://connect:8083/connectors"

echo "----------------------------------------------------"
echo "🚀 INITIALISATION DU PIPELINE BIG DATA"
echo "----------------------------------------------------"

# 1. INITIALISATION DES BASES DE DONNÉES (SQL)
echo "⏳ Attente de la disponibilité des bases..."

# Attente MySQL 
echo "📦 Injecting SQL -> Setting UP nanp user credentials"
mysql -h mysql -u root -pmysql --ssl=FALSE < /init_mysql.sql

# Création des tables
echo "📦 Injecting SQL -> Setting tables"
mysql -h mysql -u nanp -pnanp --ssl=FALSE < /setup_tyrok.sql

# ajout des données
# Données client
echo "📦 Injecting SQL -> Client Datas"
mysql -h mysql -u nanp -pnanp --ssl=FALSE < /insert_client.sql

# Données Product
echo "📦 Injecting SQL -> Ptoduct Datas"
mysql -h mysql -u nanp -pnanp --ssl=FALSE < /insert_product.sql

# Données Sales
echo "📦 Injecting SQL -> Sales Datas"
mysql -h mysql -u nanp -pnanp --ssl=FALSE < /insert_sales.sql

echo "✅ Bases de données prêtes."

echo -e "\n🔥 PIPELINE OPÉRATIONNEL !"

