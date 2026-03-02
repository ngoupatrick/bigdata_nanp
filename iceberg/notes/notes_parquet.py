"""
Ce script Spark lit des fichiers Parquet depuis un bucket MinIO, 
crée des vues temporaires
et exécute des requêtes SQL pour analyser les données. 
Assurez-vous que votre cluster Spark est correctement configuré pour accéder à MinIO 
et que les fichiers Parquet sont présents dans le bucket spécifié.
"""


"""
FIRST: 
    
    docker exec -it spark-master bash
    cd /opt/spark/bin

THEN:

spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
  --executor-memory 800m \
  --executor-cores 1 \
  --conf "spark.hadoop.fs.s3a.endpoint=http://minio:9000" \
  --conf "spark.hadoop.fs.s3a.access.key=admin" \
  --conf "spark.hadoop.fs.s3a.secret.key=pass" \
  --conf "spark.hadoop.fs.s3a.path.style.access=true" \
  --conf "spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem" \
  --conf "spark.sql.shuffle.partitions=2" \
  --conf "spark.sql.parquet.filterPushdown=true" \
  --conf "spark.sql.execution.arrow.pyspark.enabled=true" \
  /path/to/job/job.py
"""

# Importation de la bibliothèque SparkSession pour créer une session Spark
from pyspark.sql import SparkSession

file = "s3a://client-bucket/topics/fullfillment.TYROK.TYROK.client/year=2026/month=02/day=28/hour=15/fullfillment.TYROK.TYROK.client+0+0000000000.snappy.parquet"
file_star = "s3a://client-bucket/topics/fullfillment.TYROK.TYROK.client/year=2026/month=02/day=28/hour=15/*.parquet"

from pyspark.sql import SparkSession

# Configuration alignée sur votre fichier YAML (Master: 7077, MinIO: admin/password123)
spark = SparkSession.builder \
    .master("spark://spark-master:7077") \
    .appName("Minio-SQL-Parquet") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.executor.memory", "800m") \
    .config("spark.executor.cores", "1") \
    .config("spark.sql.shuffle.partitions", "2") \
    .config("spark.sql.parquet.filterPushdown", "true") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .getOrCreate()

print("Spark est connecté au Master et à MinIO !")

#==== ONLY ONE FILE ====
# 1. Charger les données (assurez-vous d'avoir créé le bucket 'data' dans MinIO)
df = spark.read.parquet(file)

# 2. Créer une vue temporaire pour utiliser le SQL standard
df.createOrReplaceTempView("uni_table")

# 3. Exécuter une requête SQL
result = spark.sql("""
    SELECT count(*) 
    FROM uni_table 
""")

result.show()

#==== ALL FILES ====
# 1. Charger toutes les données (assurez-vous d'avoir créé le bucket 'data' dans MinIO)
df_star = spark.read.parquet(file_star)
# 2. Créer une vue temporaire pour utiliser le SQL standard
df_star.createOrReplaceTempView("star_table")

# 3. Exécuter une requête SQL
result_star = spark.sql("""
    SELECT * 
    FROM star_table
    ORDER BY id
""")
result_star.show()

#==== Stopper la session Spark=====
spark.stop()