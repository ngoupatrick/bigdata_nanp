import os
from dotenv import load_dotenv
from quixstreams import Application
#from quixstreams.models.serializers import AvroDeserializer # Import crucial
from quixstreams.models.serializers.avro import AvroDeserializer
from quixstreams.models import SchemaRegistryClientConfig
from apprise import Apprise

# --- CONFIGURATION ---

# Configuration Kafka
BROKER_URL_BASE = 'kafka://redpanda-0:9092'
_SCHEMA_REGISTRY_URL = 'http://redpanda-0:8081'
TOPIC_NAME = 'fullfillment.REDPANDA.TYROK.client'
_CONSUMER_GROUP = 'connect-tyrok-sink-connector'
_APP_NAME = 'mysql-to-minio-monitor'
_LIMIT_MESSAGES = 10  # Nombre de messages à traiter avant d'envoyer une notification

# Charge les variables du fichier .env situé dans le même dossier
load_dotenv()

# Redpanda / Kafka
# Utilisation de os.getenv avec valeurs par défaut
REDPANDA_BROKER = os.getenv("REDPANDA_BROKER", BROKER_URL_BASE)
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", _SCHEMA_REGISTRY_URL)    
TOPIC_NAME = os.getenv("TOPIC_NAME", TOPIC_NAME)
LIMIT_MESSAGES = int(os.getenv("LIMIT_MESSAGES", _LIMIT_MESSAGES))
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", _CONSUMER_GROUP)
# https://appriseit.com/services/telegram/
# https://appriseit.com/services/gotify/
# Telegram (Format: tgram://bot_token/chat_id)
# Obtenez ces infos via @BotFather et @userinfobot sur Telegram
#TELEGRAM_URL = "tgram://123456789:ABCDEF_GHIJKL/987654321"
GOTIFY_URL = os.getenv("GOTIFY_URL")
if not GOTIFY_URL:
    raise ValueError("GOTIFY_URL est manquant dans le fichier .env")

# 1. Créer le client Schema Registry
schema_registry_client_config = SchemaRegistryClientConfig(url=SCHEMA_REGISTRY_URL)

# 2. Créer le Désérialiseur Avro
# Note: On ne passe plus le schéma en dur, il le récupère via le registre
avro_deserializer = AvroDeserializer(schema_registry_client_config=schema_registry_client_config)

# --- INITIALISATION NOTIFICATION ---
apobj = Apprise()
apobj.add(GOTIFY_URL)

# --- LOGIQUE DE TRAITEMENT ---
app = Application(
    broker_address=REDPANDA_BROKER,
    consumer_group=CONSUMER_GROUP,
    auto_offset_reset="earliest"
)

input_topic = app.topic(TOPIC_NAME, value_deserializer=avro_deserializer)
sdf = app.dataframe(input_topic)

# Variable d'état locale pour le compteur
# Note: Pour une production critique, utilisez le State Store de Quix
msg_counter = 0

def process_and_notify(value):
    global msg_counter
    msg_counter += 1
    
    print(f"Message reçu ({msg_counter}/{LIMIT_MESSAGES})")

    if msg_counter >= LIMIT_MESSAGES:
        print("🚀 Seuil atteint ! Envoi de la notification Gotify...")
        
        # Envoi de la notification
        success = apobj.notify(
            body=f"✅ Pipeline Update (generation d'un fichier parquet): {LIMIT_MESSAGES} nouveaux messages ont traversé Redpanda.\nTotal cumulé: {msg_counter}",
            title="Redpanda Monitor"
        )
        
        if success:
            # Réinitialiser le compteur après notification si vous voulez 
            # être alerté tous les 10 messages (10, 20, 30...)
            msg_counter = 0 
            #pass
        else:
            print("❌ Échec de l'envoi Telegram")

# Appliquer la fonction sur chaque message du flux
sdf.update(process_and_notify)

if __name__ == "__main__":
    print(f"Démarrage du monitoring sur le topic: {TOPIC_NAME}...")
    try:
        app.run(sdf)
    except KeyboardInterrupt:
        print("Arrêt du service.")
