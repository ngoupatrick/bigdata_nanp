import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType

# 1. Variables
subject = "bank_sandaga.SPARK-JSON.TYROK.client-value"
topic_name = "bank_sandaga.SPARK-JSON.TYROK.client"

# 1. Définition du schéma de la table 'client' à l'intérieur du message Debezium
# Le JSON Debezium ressemble à : {"after": {"id":1, "name":"...", ...}, "op": "c", ...}
client_schema = StructType([
    StructField("id", IntegerType()),
    StructField("code", StringType()),
    StructField("name", StringType()),
    StructField("actif", BooleanType())
])

# Schéma global de l'enveloppe Debezium
debezium_envelope = StructType([
    StructField("before", StringType()), # On le garde en string si on ne s'en sert pas
    StructField("after", client_schema),
    StructField("op", StringType())
])

# 2. Lecture du flux
spark = SparkSession.builder \
    .master("spark://spark-master:7077") \
    .appName("CDC_Client_Reader_JSON") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
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
    
# 3. Parsing JSON (Plus simple que l'Avro !)
parsed_df = raw_df.select(
    from_json(col("value").cast("string"), debezium_envelope).alias("payload")
)

# 4. Extraction
final_df = parsed_df.select(
    "payload.after.id",
    "payload.after.code",
    "payload.after.name",
    "payload.after.actif",
    col("payload.op").alias("operation")
)


# ==============================
# 5. Écriture (command line)
query = final_df.writeStream \
    .queryName("clients_json_table") \
    .outputMode("append") \
    .format("console") \
    .option("checkpointLocation", "/tmp/checkpoints/client_cdc") \
    .start()
    
query.awaitTermination()

# ===========================
# 5. Écriture en mémoire (pour Jupyter)
query = final_df.writeStream \
    .queryName("clients_json_table") \
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
        spark.sql("SELECT * FROM clients_json_table ORDER BY id DESC LIMIT 10").show()
        time.sleep(2)
except KeyboardInterrupt:
    print("Arrêt de l'affichage.")
    
# Liste toutes les requêtes spark actives et les stoppe
for s in spark.streams.active:
    print(f"Arrêt de la requête : {s.name}")
    s.stop()
