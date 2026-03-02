import os
import faust
import aiohttp
from datetime import datetime

# Configuration Kafka
BROKER_URL_BASE = 'kafka://redpanda-0:9092'
TOPIC_NAME = 'fullfillment.REDPANDA.TYROK.client'
FAUST_APP_NAME = 'mysql-to-minio-monitor'
# URL de votre instance ntfy auto-hébergée
NTFY_URL_BASE = "http://ntfy:80/monitoring"  # Assurez-vous que ce topic existe dans ntfy

# Configuration
# Permet de surcharger les valeurs par défaut via des variables d'environnement
BROKER_URL = os.environ.get('KAFKA_BROKER', BROKER_URL_BASE)
NTFY_URL = os.environ.get('NTFY_URL', NTFY_URL_BASE)

# Création de l'application Faust
app = faust.App(FAUST_APP_NAME, broker=BROKER_URL)


# Topic alimenté par votre connecteur MySQL (ex: Debezium)
mysql_topic = app.topic(TOPIC_NAME)

async def notify_ntfy(message, title="Pipeline Status", priority="default", tags="gear"):
    """Fonction helper pour envoyer vers ntfy auto-hébergé"""
    async with aiohttp.ClientSession() as session:
        try:
            await session.post(NTFY_URL, 
                data=message,
                headers={
                    "Title": title,
                    "Priority": priority,
                    "Tags": tags
                })
        except Exception as e:
            print(f"Erreur notification : {e}")

@app.agent(mysql_topic)
async def monitor_ingestion(stream):
    async for event in stream:
        try:
            # 1. Logique de transfert vers MinIO ici
            # success = upload_to_minio(event)
            
            # 2. Notification de santé (ex: tous les 2 messages)
            if stream.get_active_event().message.offset % 2 == 0:
                await notify_ntfy(
                    f"Pipeline MySQL -> MinIO actif. Offset: {stream.get_active_event().message.offset}",
                    title="Ingestion OK",
                    priority="low",
                    tags="white_check_mark"
                )

        except Exception as e:
            # 3. Notification d'alerte en cas d'échec
            await notify_ntfy(
                f"Échec ingestion MinIO : {str(e)}",
                title="PIPELINE ERROR",
                priority="high",
                tags="rotating_light,skull"
            )
