
"""
Iceberg ne remplace pas Parquet, il l'organise.
Parquet est un format de stockage de données en colonnes,
tandis qu'Iceberg est une couche de gestion de données qui peut utiliser Parquet comme format de stockage sous-jacent.
Iceberg offre des fonctionnalités avancées telles que la gestion des versions, les transactions ACID, et la possibilité de gérer de grandes quantités de données avec des performances optimisées.
Iceberg:
- Gère les métadonnées de manière efficace, permettant des opérations rapides sur les données.
- Supporte les transactions ACID, garantissant la cohérence des données même en cas de pannes.
- Permet de gérer les données à grande échelle, avec des fonctionnalités de partitionnement et de clustering pour améliorer les performances des requêtes.
- Offre une compatibilité avec plusieurs moteurs de traitement de données, tels que Spark, Trino, et Flink, facilitant ainsi l'intégration dans différents écosystèmes de données.
"""

"""
Transactions ACID : Plusieurs utilisateurs peuvent lire/écrire simultanément sans corruption.
Gestion des versions : Permet de revenir à des versions précédentes des données.
Partitionnement : Améliore les performances en organisant les données de manière intelligente.
Clustering : Regroupe les données similaires pour accélérer les requêtes.
"""

"""
Iceberg - Parquet
Migrer: transformer définitivement
Snapshot: créer une vue Iceberg sans toucher aux fichiers originaux
"""

"""
first and foremost, check that the jars are available in the Spark worker nodes. 
You can do this by running the following command in your Jupyter notebook:
!ls /home/jovyan/.ivy2/jars

result should include the following jars:
com.amazonaws_aws-java-sdk-bundle-1.12.262.jar
org.apache.hadoop_hadoop-aws-3.3.4.jar
org.apache.iceberg_iceberg-spark-runtime-3.4_2.12-1.3.1.jar
org.wildfly.openssl_wildfly-openssl-1.0.7.Final.jar
"""


from pyspark.sql import SparkSession

"""
base_bucket: bucket S3 où sont stockées les données Parquet
meta_bucket: bucket S3 où Iceberg stocke les métadonnées de la table
db_name: nom du catalogue Iceberg
schema_name: nom de la base de données dans le catalogue
table_name: nom de la table Iceberg
"""
base_bucket = "s3a://client-bucket/"
meta_bucket = "s3a://tyrok-bucket/"
db_name = "minio_catalog"
schema_name = "db"
table_name = "client_full"

"""
Configuration alignée sur votre fichier YAML (Master: 7077, MinIO: admin/password123)
- spark.jars.packages : Ajout des dépendances nécessaires pour Iceberg et S3
- spark.sql.extensions : Extension pour activer les fonctionnalités d'Iceberg
- spark.sql.catalog.minio_catalog : Configuration du catalogue Iceberg pour utiliser MinIO
- spark.hadoop.fs.s3a.* : Configuration pour accéder à MinIO via le protocole s3a
- spark.executor.memory et spark.executor.cores : Configuration des ressources pour les tâches Spark
- spark.sql.shuffle.partitions : Réduction du nombre de partitions pour les opérations de shuffle
- spark.sql.parquet.filterPushdown : Activation du pushdown des filtres pour les fichiers Parquet
- spark.sql.execution.arrow.pyspark.enabled : Activation de l'exécution Arrow pour améliorer les performances des opérations PySpark
"""

# Configuration alignée sur votre fichier YAML (Master: 7077, MinIO: admin/password123)
spark = SparkSession.builder \
    .master("spark://spark-master:7077") \
    .appName("Iceberg-MinIO-Parquet") \
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.3.1,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.minio_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.minio_catalog.type", "hadoop") \
    .config("spark.sql.catalog.minio_catalog.warehouse", meta_bucket+"warehouse") \
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

print("✅ Session Spark initialisée avec Iceberg !")

#==== Namespace et base de données ====
# Créer une base de données dans ce catalogue
spark.sql(f"""
          CREATE DATABASE IF NOT EXISTS {db_name}.{schema_name}
        """)

# verifier que le namespace a été créé
spark.sql(f"""
    SHOW NAMESPACES IN {db_name}
""").show()

# verifier que la base de données a été créée
spark.sql(f"""
    SHOW DATABASES IN {db_name}
""").show()

#==== Table Iceberg ====
# Créer une table Iceberg à partir de vos données Parquet existantes
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {db_name}.{schema_name}.{table_name} (
        id bigint,
        code string,
        name string,
        actif int,
        year string,
        month string,
        day string,
        hour string
    )
    USING iceberg
    PARTITIONED BY (year, month, day, hour)
""")

# verifier que la table a été créée
spark.sql(f"""
    SHOW TABLES IN {db_name}.{schema_name}
""").show()

#Voir les données (table vide car pas de snapshot ou ajout de fichier parquet dans les metadonnées Iceberg)
spark.sql("""
SELECT * 
FROM minio_catalog.db.client_full
ORDER BY id
""").show()

#==== add_files ====
# Ajouter les fichiers Parquet existants à la table Iceberg
spark.sql(f"""
    CALL {db_name}.system.add_files(
        table => '{db_name}.{schema_name}.{table_name}',
        source_table => 'parquet.`{base_bucket}`'
    )
""")

#Voir la liste des fichiers physiques indexés par Iceberg
spark.sql(f"""
    SELECT file_path, partition, file_size_in_bytes 
    FROM {db_name}.{schema_name}.{table_name}.files
""").show()

# verifier que les fichiers ont été ajoutés
spark.sql(f"""
    SELECT * 
    FROM {db_name}.{schema_name}.{table_name}
    LIMIT 10
""").show()

#==== Optimisations (cron ou airflow) ====
# Comme vous créez des dossiers par Heure, 
# vous allez vous retrouver avec des milliers de petits fichiers Parquet
# ce qui tue les performances SQL
# Iceberg va vous permettre de faire du compaction (fusionner les petits fichiers en plus gros fichiers)
# Executer la requete suivante une fois par jour pour compacter les fichiers de la table client_full
spark.sql(f"""
    CALL {db_name}.system.rewrite_data_files(
        table => '{db_name}.{schema_name}.{table_name}',
        strategy => 'binpack',
        options => map('target-file-size-bytes', '134217728') -- 128 Mo
    )
""")

#==== Requêtes SQL ====
# Exécuter une requête SQL sur la table Iceberg
result = spark.sql(f"""
    SELECT year, month, day, hour, count(*) as count
    FROM {db_name}.{schema_name}.{table_name}
    GROUP BY year, month, day, hour
    ORDER BY year, month, day, hour
""")
result.show()

#==== Requêtes SQL avec filtre ====
# Exécuter une requête SQL avec un filtre sur la table Iceberg
result_filtered = spark.sql(f"""
    SELECT year, month, day, hour, count(*) as count
    FROM {db_name}.{schema_name}.{table_name}
    WHERE year = '2026' AND month = '02' AND day = '28' AND hour = '15'
    GROUP BY year, month, day, hour
""")
result_filtered.show()

#==== Requêtes SQL avec filtre sur les partitions ====
# Exécuter une requête SQL avec un filtre sur les partitions de la table Iceberg
result_partition_filtered = spark.sql(f"""
    SELECT year, month, day, hour, count(*) as count
    FROM {db_name}.{schema_name}.{table_name}
    WHERE year = '2026' AND month = '02' AND day = '28' AND hour = '15'
    GROUP BY year, month, day, hour
""")
result_partition_filtered.show()


#==== Stopper la session Spark=====
spark.stop()