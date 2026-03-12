FROM debezium/connect:2.7.3.Final

USER root

# 1. Installation de unzip pour le connecteur S3
RUN microdnf install -y unzip

# 2. NETTOYAGE : Supprime tous les connecteurs sauf MySQL et Postgres
# On garde uniquement les répertoires contenant "mysql" ou "postgres" dans /kafka/connect
RUN find /kafka/connect -mindepth 1 -maxdepth 1 -type d \
    ! -name "*mysql*"  ! -name "*avro*" \
    -exec rm -rf {} +

COPY ./plugins/confluentinc-kafka-connect-avro-converter-8.1.1.zip /tmp/avro.zip

# 4. EXTRACTION dans le répertoire des plugins de Kafka Connect
RUN unzip /tmp/avro.zip -d /kafka/connect/ \
    && rm /tmp/avro.zip \
    && chown -R kafka:kafka /kafka/connect/

# 4. Permissions pour l'utilisateur kafka
RUN chown -R kafka:kafka /kafka/connect/

USER kafka
