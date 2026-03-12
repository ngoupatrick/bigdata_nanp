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

echo "✅ Bases de données prêtes."

# 2. CONFIGURATION DES CONNECTEURS DEBEZIUM
echo "⏳ Attente de l'API Debezium Connect..."
echo "🔗 Enregistrement des connecteurs..."

# SOURCE : MySQL: Avro
echo "🔗 Enregistrement du connecteur Mysql Avro..."
curl -i -X POST -H "Content-Type:application/json" \
    -d @tyrok-source-connector.json \
    $CONNECT_URL

# SOURCE : MySQL: JSON
echo "🔗 Enregistrement du connecteur Mysql Avro..."
curl -i -X POST -H "Content-Type:application/json" \
    -d @tyrok-source-connector-json.json \
    $CONNECT_URL

echo -e "\n🔥 PIPELINE OPÉRATIONNEL !"

