from pyspark.sql import SparkSession
import sys

def main():
    # L'appName peut être défini ici ou via --name dans spark-submit
    spark = SparkSession.builder \
        .appName("Minio-SQL-Processing") \
        .getOrCreate()

    # Log pour vérifier que la session est active
    print("--- Session Spark démarrée avec succès ---")

    try:
        # 1. Lecture des données depuis MinIO
        # Le chemin s3a:// est résolu grâce aux confs de spark-submit
        input_path = "s3a://warehouse/input_data.parquet"
        print(f"--- Lecture : {input_path} ---")
        
        df = spark.read.parquet(input_path)

        # 2. Transformation simple (Exemple : compter par catégorie)
        df_result = df.groupBy("Categorie").count()

        # 3. Affichage du résultat dans les logs du cluster
        df_result.show()

        # 4. Écriture du résultat (Optionnel)
        output_path = "s3a://warehouse/results/count_output"
        df_result.write.mode("overwrite").parquet(output_path)
        print(f"--- Succès ! Résultat écrit dans : {output_path} ---")

    except Exception as e:
        print(f"!!! Erreur pendant le job : {e}")
        sys.exit(1)

    finally:
        spark.stop()
        print("--- Session Spark arrêtée ---")

if __name__ == "__main__":
    main()
