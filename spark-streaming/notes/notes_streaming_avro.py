import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.avro.functions import from_avro

# 1. Récupérer le schéma JSON depuis le Schema Registry de Redpanda
# Le sujet est généralement "nom_du_topic-value"
subject = "bank_sandaga.SPARK.TYROK.client-value"
topic_name = "bank_sandaga.SPARK.TYROK.client"
schema_url = f"http://redpanda-0:8081/subjects/{subject}/versions/latest"

res = requests.get(schema_url).json()
avro_schema_json = res['schema']

# 2. Lecture du flux
spark = SparkSession.builder \
    .master("spark://spark-master:7077") \
    .appName("CDC_Client_Reader") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.apache.spark:spark-avro_2.12:3.4.0") \
    .config("spark.executor.memory", "800m") \
    .config("spark.executor.cores", "1") \
    .config("spark.sql.shuffle.partitions", "2") \
    .config("spark.sql.parquet.filterPushdown", "true") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .getOrCreate()

# ====== NOT READING FROM BEGINING
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "redpanda-0:9092") \
    .option("subscribe", topic_name) \
    .load()
    
# ====== READ FROM BEGINING
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "redpanda-0:9092") \
    .option("subscribe", topic_name) \
    .option("startingOffsets", "earliest") \
    .load()


# 3. Désérialisation (en ignorant les 5 premiers octets d'en-tête de Confluent Avro)
# On utilise substring(col("value"), 6, ...) car l'Avro de Kafka contient un Magic Byte + Schema ID
decoded_df = raw_df.select(
    from_avro(col("value").substr(6, 1000000), avro_schema_json).alias("payload")
)

# 4. Extraction des colonnes de la table 'client'
final_df = decoded_df.select(
    col("payload.after.id").alias("id"),
    col("payload.after.code").alias("code"),
    col("payload.after.name").alias("name"),
    col("payload.after.actif").alias("actif"),
    col("payload.op").alias("operation_type")
)

# ==============================
# 5. Écriture (command line)
query = final_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("checkpointLocation", "/tmp/checkpoints/client_cdc") \
    .start()

query.awaitTermination()

# ===========================
# 1. Écrire le flux dans une table temporaire en mémoire (notebook)
query = final_df.writeStream \
    .queryName("clients_table") \
    .outputMode("append") \
    .format("memory") \
    .start()
    
# 2. Afficher le contenu de la table (exécute cette cellule plusieurs fois)
import time
from IPython.display import display, clear_output

try:
    while True:
        clear_output(wait=True)
        print("Dernières données reçues depuis Redpanda :")
        spark.sql("SELECT * FROM clients_table ORDER BY id DESC LIMIT 10").show()
        time.sleep(2)
except KeyboardInterrupt:
    print("Arrêt de l'affichage.")
    
# Liste toutes les requêtes spark actives et les stoppe
for s in spark.streams.active:
    print(f"Arrêt de la requête : {s.name}")
    s.stop()
