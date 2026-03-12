# 🦞 bigdata_nanp - KAFKA (REDPANDA) — BigData streaming stack

Streaming pipeline to ingest datas from `MYSQL` and store them into `.parquet` format in `MINIO bucket` (bucket: `client-redpanda`)

<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/flow_streaming.drawio.png">
        <img src="images/flow_streaming.drawio.png" alt="BigData streaming stack (docker)" width="600" height="300">
    </picture>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

---

**Stack** is a simple *BigData streaming stack* running over *Docker*.

It will help you to deploy and test a simple **Streaming** pipeline using **Docker** and **kafka**.

---

**Note: you don't need all this components. the most usefull are `mysql, minio, redpanda-0, connect`.**

## **Components:**

- **mysql:** contains database `TYROK`
- **kafka cluster:** Spread over three nodes (`redpanda-0`, `redpanda-1`, `redpanda-2`). used to ingest tables `client`, `product`, `sales`. `redpanda-0` act as `master node` and the two others as `slave nodes`. **NOTES:** If it's take too much resources, comment or shutdown `redpanda-1` and `redpanda-2`
- **redpanda-console:** UI used to manage kafka (redpanda) cluster `[Topics, Connectors, Consumer Groups]`.
- **minio:** store result in `parquet` format. It use bucket `client-redpanda`.
- **connect:** used to launch `source (mysql, debezium, tyrok-source-connector.json)` and `sink (S3, confluent, tyrok-sink-connector.json) connectors`.
- **notifier-service:** used to `monitoring` kafka topics and send `alert` to app like `slack or telegram` (in this case `gotify`)
- **gotify:** Notification app client like `slack or telegram`.
- **setup-automation:** used to `initialize Mysql (User, databases and tables)`, and also `launch connectors source and sink`. You can disable it before launching the stack (there for, you must absolutly launch connect throw command line).
- **streamlit_app:** `Client App for Mysql`. You can find `code in folder python/streamlit`.
- **streamlit-dashboard:** `Client App for Minio`. used to see every datas push inside `Minio bucket client-redpanda` with some `stats`. You can find `code in folder python/streamlit-result`.
- **python_base:** Container used to interact with `Mysql (folder python/python_mysql)` and `Minio (folder python/python_minio)`.

---

## **Files & Folders:**

1- **images:** contains screenshot.

2- **notes:** notes and trash infos.

3- **plugins:** contains 3 files, but only 2 are usefull.

- `confluentinc-kafka-connect-avro-converter-8.1.1.zip`: install inside `connect container`. Provide class to implement `Avro` data manipulation.

- `confluentinc-kafka-connect-s3-10.5.13.zip`: install inside `connect container`. Provide class to implement `Sink to S3`.

- `confluentinc-kafka-connect-avro-converter-7.5.0.zip`: Same as 1-, but an older version.

4- **python:** contains five folders:

- `python_mysql`: scripts used to add and list data in mysql

- `python_minio`: scripts used to add, list and read parquet inside minio bucket.

- `notifier`: scripts used to send notification a client like `Telegram, Slack`. In this case we use `GOTIFY`

- `streamlit`: UI to interact with `MYSQL tables`, like an app install on a `client side`. used to populate (simulate) datas

- `streamlit-result`: UI to read datas ingest throw `KAFKA in MINIO`. it's refresh every `15s`.

5- **scripts:** folder For `setup-automation coontainer`, contains 4 files:

- `Dockerfile`: Base on `image alpine:latest`, install libs like `curl, bash and mysql-client`. Workdir `/`, all scripts used to initialize others components reside in this folder inside docker container.

- `init_mysql.sql`: Code SQL to config User `nanp` .

```sql
-- 1. Droits de réplication pour MySQL 8.0 (Indispensable pour Debezium)
GRANT ALL PRIVILEGES ON *.* TO 'nanp'@'%';
-- GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'nanp'@'%';
FLUSH PRIVILEGES;
```

- `setup_tyrok.sql`: Code SQL intialize databases and tables.

```sql
-- Création de la base de données
CREATE DATABASE IF NOT EXISTS TYROK;
USE TYROK;

-- Création de la table 'client'
CREATE TABLE IF NOT EXISTS client (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    actif BOOLEAN DEFAULT TRUE
);

-- Création de la table 'product'
CREATE TABLE IF NOT EXISTS product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    pu DECIMAL(10, 2) -- Utilisation de DECIMAL pour plus de précision monétaire
);

-- Création de la table 'sales'
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_client INT NOT NULL,
    id_product INT NOT NULL,
    qte INT NOT NULL,
    total DECIMAL(12, 2),
    
    -- Définition des clés étrangères
    CONSTRAINT fk_client FOREIGN KEY (id_client) REFERENCES client(id),
    CONSTRAINT fk_product FOREIGN KEY (id_product) REFERENCES product(id)
);
```

- `setup_pipeline.sh`: Shell script used to run `.sql files` and `deploy sink and source connectors`.

```sh
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

# SINK : Minio: Parquet
echo "🔗 Enregistrement du connecteur Sink vers Minio Bucket: redpanda-bucket..."
curl -i -X POST -H "Content-Type:application/json" \
    -d @tyrok-sink-connector.json \
    $CONNECT_URL

echo -e "\n🔥 PIPELINE OPÉRATIONNEL !"
```

6- **config.yml:** config use by `redpanda-console container` to connect to `kafka cluster`. Sample file is **`redpanda-console-config.yaml`**

7- **tyrok-source-connector.json & tyrok-sink-connector.json:** config used to deploy source and sink connectors

---

## **PORTS & configs**

- **Mysql**: Default -> `3306`, Exposed -> `8889`
- **redpanda-console**: Default (http) -> `8080`, Exposed(http) -> `8100`. **`[http://localhost:8100]`**
- **Minio API S3**: Default -> `9000`, Exposed -> `9030`
- **Minio UI**: Default -> `9001`, Exposed -> `9031`. **`[http://localhost:9031]`**
- **connect API Rest**: Default -> `8083`, Exposed -> `8093`
- **gotify UI**: Default -> `80`, Exposed -> `8023`. **`[http://localhost:8023]`**
- **streamlit_app UI**: Default -> `8501`, Exposed -> `8561`. **`[http://localhost:8561]`**
- **streamlit-dashboard UI**: Default -> `8501`, Exposed -> `8551`. **`[http://localhost:8551]`**

---

### **Volumes**
before you start the docker stack, make sure to change volumes locations

```yml

volumes:
  mysql_data:
    driver: local # Define the driver and options under the volume name
    driver_opts:
      type: none
      device: /Change/Path/mysql
      o: bind
  minio_data:
    driver: local # Define the driver and options under the volume name
    driver_opts:
      type: none
      device: /Change/Path/minio
      o: bind  
  gotify_data:
    driver: local # Define the driver and options under the volume name
    driver_opts:
      type: none
      device: /Change/Path/gotify
      o: bind
  redpanda-0:
    driver: local # Define the driver and options under the volume name
    driver_opts:
      type: none
      device: /Change/Path/redpanda/redpanda-0
      o: bind
  redpanda-1:
    driver: local # Define the driver and options under the volume name
    driver_opts:
      type: none
      device: /Change/Path/redpanda/redpanda-1
      o: bind
  redpanda-2:
    driver: local # Define the driver and options under the volume name
    driver_opts:
      type: none
      device: /Change/Path/redpanda/redpanda-2
      o: bind
  share_data:
    driver: local # Define the driver and options under the volume name
    driver_opts:
      type: none
      device: /Change/Path/share_folder
      o: bind

```

---

### **Configs & setup**

* #### **Step 1:** Create all volumes folders inside your main host (see volumes above)

* #### **step 2:** Clone the repo and move to folder **`redpanda_stream`**

* #### **step 3:** Change volumes path inside **`compose.yml`** file under section **`volumes:`** (see above)

* #### **step 4:** Set up Kafka console web UI. Configs file **`config.yml`**.

  * ##### **`brokers`:** list of existing brokers (use service hostname)

  ```yml
  kafka:
    # Brokers is a list of bootstrap servers with ports.
    brokers:
      - "redpanda-0:9092"
  ```

  * ##### **`schemaRegistry`:** Schema registration, Redpanda already have one

  ```yml
  schemaRegistry:
    enabled: true
    urls:
      - "http://redpanda-0:8081"
  ```

  * ##### **`kafkaConnect`:** We are going to use our own **`connector service`** (inside **`compose.yml`**), not a redpanda well knowned connector

  ```yml
  #----------------------------------------------------------------------------
  # Kafka Connect configuration (configuration for connecting to external Kafka Connect clusters, not Redpanda Connect)
  #----------------------------------------------------------------------------
  kafkaConnect:
    enabled: true
    clusters:    
      - name: my-connect-cluster # this will appear in redpanda console
        url: "http://connect:8083" # service hostname under compose.yml
  ```

* #### **step 5:** Set up Mysql. Configs file **`my-custom.cnf`**. Make sure you have these lines (it's help kafka connector to track changes or CDC inside Mysql, every operations are capture by bin logs files).

```conf
default-authentication-plugin=mysql_native_password
# 1. Enable Binary Logging
log-bin=mysql-bin
binlog_format=ROW
binlog_row_image=FULL

# 2. Server ID (Must be unique within your replication topology)
# will be used by kafka connect
server-id=1

# 3. GTID Mode (Recommended for recovery and consistency)
# not so much usefull in this case
gtid_mode=ON
enforce_gtid_consistency=ON
```

* #### **step 6:** Set up Minio alias. Inside **`compose.yml`**, take note of the **`command`** section under **`minio service`**. aliases are generally used to run **`mc commands`**. In this case, alias name is **`myalias`**.

```yml
command: >
    "minio server /data --console-address ':9001' & 
     sleep 5; 
     mc alias set myalias http://localhost:9000 admin password123;
     wait"
```

* #### **step 7:** Set up Notifier env file. under folder **`python/notifier`** Rename **`.env.example`** to **`.env`**. Then change **`GOTIFY_URL`** and **`LIMIT_MESSAGES`** values.

```makefile
# syntax URL gotify://gotify/[key_channel]
# the key_channel is generated on gotify UI [http://localhost:8023/]
GOTIFY_URL=gotify://gotify/A_dT4Gc-u-Mp3Ei
# LIMIT_MESSAGES mean that, every 4 messages going throw Kafka, you will receive a notification
LIMIT_MESSAGES=4
```

* #### **step 8:** Set up Streamlit-app and streamlit Dashboard env files. under folder **`python/streamlit`** and **`python/streamlit-result`** Rename each **`.env.example`** to **`.env`**. Now you can apply some changes if you want to.

* #### **step 9:** Set up Source Mysql json connector. Config file **`tyrok-source-connector.json`**.

  * ##### **`"database.hostname": "mysql",`** | **`"database.port": "3306",`** => Mysql host location

  * ##### **`"database.user": "nanp"`** | **`"database.password": "nanp",`** => Mysql credentials

  * ##### **`"database.server.id": "1",`** | **`"database.include.list": "TYROK",`** | **`"table.include.list": "TYROK.client",`** => Databases and tables ingested

  * ##### **`"topic.creation.enable": true,`** => Will create topic if doesn't exists in kafka

  * ##### **`"topic.creation.default.partitions": "1",`** | **`"topic.creation.default.replication.factor": "1",`** => Replication factor accross kafka cluster

* #### **step 10:** Set up Sink Minio json connector. Config file **`tyrok-sink-connector.json`**.

  * ##### **`"tasks.max": "2",`** => Concurent tasks used to ingest data

  * ##### **`"store.url": "http://minio:9000",`** | **`"s3.bucket.name": "client-redpanda",`** | **`"s3.region": "us-east-1",`** => Minio Dest location

  * ##### **`"aws.access.key.id": "admin",`** | **`"aws.secret.access.key": "password123",`** => Minio Credentials

  * ##### **`"format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",`** | **`"parquet.codec": "snappy",`** => files format and compression of parquet files in minio

  * ##### **`"partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",`** | **`"path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",`** => will store data in minio folder with partitions Year, Month, Day and Hour

* #### **step 11:** Start your project inside **`compose.yml`**.

```sh
# Be sure to be in the folder with compose.yml file
# start all
docker compose up -d
```


---

### **Run project & some cleaning ops**

```sh
# Be sure to be in the folder with compose.yml file
# start all
docker compose up -d

# stop all and clean some volume
docker compose down -v --remove-orphans
```

---

### **Troubleshooting**

* #### **clean all data in redpanda:** you can use **`setup-automation`** container to redeploy Sink and source connector.

```sh
# 1- stop all and clean some volume
docker compose down -v --remove-orphans
# 2- clean folders
sudo rm -rf /Change/Path/redpanda/redpanda-0/*
sudo rm -rf /Change/Path/redpanda/redpanda-1/*
sudo rm -rf /Change/Path/redpanda/redpanda-2/*
```

* #### **clean all data in mysql:** you can use **`setup-automation`** container to recreate all databases and tables.

```sh
# 1- stop all and clean some volume
docker compose down -v --remove-orphans
# 2- clean folders
sudo rm -rf /Change/Path/mysql/*
```

* #### **delete minio bucket:** you can use **minio UI** container to recreate all bucket.

```sh
# delete a bucket
docker exec minio mc rb --force myalias/[nom-du-bucket]
```

---

### **Some commands**

* #### **Kafka:**

You can use [`rpk documentation`](https://docs.redpanda.com/current/get-started/intro-to-rpk/ "rpk commands") or spin of kafka client service in your `compose.yml` file.

* #### **Connector:**

```sh
# FROM YOUR HOST SYSTEM
# list of plugins available inside connector
curl -s -X GET http://localhost:8093/connector-plugins | jq '.[].class'

# deploy source connector
curl -X POST http://localhost:8093/connectors -H "Content-Type: application/json" -d @tyrok-source-connector.json

# deploy sink connector
curl -X POST http://localhost:8093/connectors -H "Content-Type: application/json" -d @tyrok-sink-connector.json

# list of deployed connectors
curl -s http://localhost:8093/connectors | jq

# check status of each connectors
curl -s http://localhost:8093/connectors/tyrok-source-connector/status | jq
curl -s http://localhost:8093/connectors/tyrok-sink-connector/status | jq

# pause a connector
curl -X PUT http://localhost:8093/connectors/{connector_name}/pause

# resume a connector
curl -X PUT http://localhost:8093/connectors/{connector_name}/resume

# clean & delete a connector (usefull when you want to restart ingestion)
# !!Caution: before use this, clean redpanda volumes and minio bucket (client-redpanda)
curl -X PUT http://localhost:8093/connectors/{connector_name}/stop
curl -X DELETE http://localhost:8093/connectors/{connector_name}/offsets
curl -X DELETE http://localhost:8093/connectors/{connector_name}

```

---

## **Project**

- ### **mysql**
make sur you create all databases and tables or use `setup-automation coontainer`

- ### **minio**
url: **`http://localhost:9031/`**
create bucket `client-redpanda`

- ### **python**
`See main page`, for more infos

#### mysql

```bash
# first, make sure your in python container
docker exec -it python_base bash

# move to '/app/python_mysql'
cd /app/python_mysql

# commands helps
python main.py --help

# test connexion
python main.py test

# list datas
python main.py list client
python main.py list product
python main.py list sales

# add datas
python main.py client --code "C003" --name "Entreprise XYZ"
python main.py product --code "P-TAB" --name "Tablette" --pu 299.99
python main.py sale --client_id 1 --product_id 2 --qte 3 --total 899.97
```

#### minio

```bash
# before, make sure to modify '.env' file

# first, make sure your in python container
docker exec -it python_base bash

# move to '/app/python_minio'
cd /app/python_minio

# commands helps
python main.py --help

# list bucket content
python main.py list --bucket my-bucket

# list all files in a bucket
python main.py list-all --bucket my-bucket

# count files in bucket
python main.py count --bucket my-bucket

# read parquet or csv file
python main.py read --bucket my-bucket --file data.csv --style fancy_grid
python main.py read --bucket my-bucket --file data.parquet --style fancy_grid

# read all parquet or csv file
python main.py read-all --bucket my-bucket --style fancy_grid

# add file in bucket
python main.py put --bucket my-bucket --local /path/to/local/file

```

* ### **Container:** Deployed containers

<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/portainer_containers.png">
        <img src="images/portainer_containers.png" alt="Containers list" width="500" height="400">
    </picture>
  </p>

* ### **Kafka Cluster**

  * **console**: **`https://localhost:8100/`** 

  <p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/redpanda_cluster_details.png">
        <img src="images/redpanda_cluster_details.png" alt="Redpanda console Cluster Details" width="500" height="400">
    </picture>
  </p>

  * **nodes or borkers:** **`redpanda-0 (master), redpanda-1 & 2 (slaves)`**

  <p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/redpanda_overview.png">
        <img src="images/redpanda_overview.png" alt="Redpanda console Overview" width="500" height="400">
    </picture>
  </p>

  * **Resources config:** in .yml file, option `--smp 1` means 1 cores. option `--memory 1G` means 1G RAM allocate. You can tune them.

  * **Client Topic:** `bank_sandaga.REDPANDA.TYROK.client`.

  <p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/redpanda_topics.png">
        <img src="images/redpanda_topics.png" alt="Redpanda console Overview" width="500" height="300">
    </picture>
  </p>


* ### **Connect:**

<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/redpanda_connect.png">
        <img src="images/redpanda_connect.png" alt="Redpanda console Overview" width="500" height="300">
    </picture>
</p>

  * **`BOOTSTRAP_SERVERS: redpanda-1:9092,redpanda-2:9092,redpanda-0:9092`**: kafka addresses

  * **`Dockerfile`**: 

    * use base image `debezium/connect:2.7.3.Final`

    ```bash
    FROM debezium/connect:2.7.3.Final

    USER root

    # 1. Installation de unzip pour le connecteur S3
    RUN microdnf install -y unzip
    ```

    * Remove unecessary plugins

    ```bash
    RUN find /kafka/connect -mindepth 1 -maxdepth 1 -type d \
      ! -name "*mysql*" ! -name "*postgres*"  ! -name "*avro*" \
      -exec rm -rf {} +
    ```

    * install **[S3 Plugin](https://d2p6pa21dvn84.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.5.13/confluentinc-kafka-connect-s3-10.5.13.zip)** and Avro plugins


    ```bash
    COPY ./plugins/confluentinc-kafka-connect-s3-10.5.13.zip /tmp/s3.zip
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
    ```

* ### **Minio:** Parquet files

<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/minio-parquet.png">
        <img src="images/minio-parquet.png" alt="Containers list" width="500" height="300">
    </picture>
</p>

* ### **Streamlit - client & Dashboard:** 

<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/client_ui.png">
        <img src="images/client_ui.png" alt="Containers list" width="500" height="300">
    </picture>
</p>

<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/consumer_ui.png">
        <img src="images/consumer_ui.png" alt="Containers list" width="500" height="300">
    </picture>
</p>

* ### **Gotify notification:** 

<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/gotify.png">
        <img src="images/gotify.png" alt="Containers list" width="400" height="200">
    </picture>
</p>


Enjoy!


