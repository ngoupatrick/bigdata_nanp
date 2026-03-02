FROM debezium/connect:2.7.3.Final

USER root

# 1. Installation de unzip pour le connecteur S3
RUN microdnf install -y unzip

# 2. NETTOYAGE : Supprime tous les connecteurs sauf MySQL et Postgres
# On garde uniquement les répertoires contenant "mysql" ou "postgres" dans /kafka/connect
RUN find /kafka/connect -mindepth 1 -maxdepth 1 -type d \
    ! -name "*mysql*" ! -name "*postgres*"  ! -name "*avro*" \
    -exec rm -rf {} +

# plugins disponibles :
#   https://www.confluent.io/hub/confluentinc/kafka-connect-s3
#   https://d2p6pa21dvn84.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.5.13/confluentinc-kafka-connect-s3-10.5.13.zip
# 3. AJOUT SINK S3 : Téléchargement et installation du connecteur Confluent S3
#RUN wget --tries=3 --no-check-certificate https://d2p6pa21dvn84.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.5.13/confluentinc-kafka-connect-s3-10.5.13.zip \
#    -O /tmp/s3.zip \
#    && unzip /tmp/s3.zip -d /kafka/connect/ \
#    && rm /tmp/s3.zip
# 3. INSTALLATION S3 : Copie locale (Plus de wget/curl/DNS)
COPY ./plugins/confluentinc-kafka-connect-s3-10.5.13.zip /tmp/s3.zip
#COPY ./plugins/confluentinc-kafka-connect-avro-converter-7.5.0.zip /tmp/avro.zip
COPY ./plugins/confluentinc-kafka-connect-avro-converter-8.1.1.zip /tmp/avro.zip

# 4. EXTRACTION dans le répertoire des plugins de Kafka Connect
RUN unzip /tmp/s3.zip -d /kafka/connect/ \
    && rm /tmp/s3.zip \
    && chown -R kafka:kafka /kafka/connect/

RUN unzip /tmp/avro.zip -d /kafka/connect/ \
    && rm /tmp/avro.zip \
    && chown -R kafka:kafka /kafka/connect/

# 4. Permissions pour l'utilisateur kafka
RUN chown -R kafka:kafka /kafka/connect/

USER kafka
