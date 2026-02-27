# 🦞 bigdata_nanp - NIFI — BigData batch stack
bigdata tps and stuffs

<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/archi-nifi.drawio.png">
        <img src="images/archi-nifi.drawio.png" alt="BigData stream stack (docker)" width="300" height="300">
    </picture>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

---

**Stack** is a simple *BigData batch stack* running over *Docker*.

It will help you to deploy and test a simple **Batch** pipeline using **Docker** and **nifi**.

**Components:**
- **Mysql:** contains database `TYROK`
- **NIFI:** use to ingest tables `client`, `product`, `sales`
- **MINIO:** store result in `parquet` format. It use buckets `[client/product/sales]-bucket`
- **PYTHON:** contains two folders:

1- `python_mysql`: scripts use to add and list data in mysql

2- `python_minio`: scripts use to add, list, read parquet and bucket in minio

## PORTS & configs

- **Mysql**: Default -> `3306`, Exposed -> `8889`
- **Nifi**: Default (http,https) -> `8080,8443`, Exposed(http,https) -> `8887,8443`
- **Minio API S3**: Default -> `9000`, Exposed -> `9030`
- **Minio UI**: Default -> `9001`, Exposed -> `9031`

---

### Volumes
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
  share_data:
    driver: local # Define the driver and options under the volume name
    driver_opts:
      type: none
      device: /Change/Path/share_folder
      o: bind

```

---

### Run project & some cleaning ops

```sh
# Be sure to be in the folder with compose.yml file
# start all
docker compose up -d

# stop all and clean some volume
docker compose down -v --remove-orphans
```

---

## Project

### - mysql
make sur you create all databases and tables

### - minio
url: http://localhost:9031/
create all buckets

### - python
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

# count files in bucket
python main.py count --bucket my-bucket

# read parquet or csv file
python main.py read --bucket my-bucket --file data.csv --style fancy_grid
python main.py read --bucket my-bucket --file data.parquet --style fancy_grid

# add file in bucket
python main.py put --bucket my-bucket --local /path/to/local/file

```

#### nifi
0- url: https://localhost:8443/nifi/login

1- just import template `mysql-nifi-minio.xml`

2- change username and password in `QueryDatabaseTablerecord` and `PutS3Object`

3- create `jars` folder inside your `share_data` volume and copy all jars files inside

4- some config settings: 

Pool connection -> **Database Connection URL**: `jdbc:mysql://mysql:3306/TYROK`

Pool connection -> **Database Driver ClassName**: `com.mysql.jdbc.Driver`

Pool connection -> **Database Driver Location(s)**: `/partage/jars/mysql-connector-java-8.0.30.jar`

update attribute -> **filename**: `client_${now():format('yyyyMMdd_HHmmss')}.parquet`

PutS3Oject -> **EndPoint Override URL**: `http://minio:9000`


<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light dark)" srcset="images/1-mysql-nifi-minio.png">
        <img src="images/1-mysql-nifi-minio.png" alt="BigData stream stack (docker)" width="600" height="700">
    </picture>
</p>




