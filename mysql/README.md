# 🦞 bigdata_nanp - MYSQL — BigData stack
bigdata tps and stuffs

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

**User:** `nanp` (you can change it from each `compose.yml` files)
**Database:** `TYROK`
**mysql client**: https://dbeaver.io/ or `SHELL`

---

### scripts (`setup_tyrok.sql`)

```sql
-- DB creation
CREATE DATABASE IF NOT EXISTS TYROK;
USE TYROK;
```

```sql
-- client table
CREATE TABLE client (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    actif BOOLEAN DEFAULT TRUE
);
```

```sql
-- product table
CREATE TABLE product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    pu DECIMAL(10, 2) -- Utilisation de DECIMAL pour plus de précision monétaire
);
```

```sql
-- sales table
CREATE TABLE sales (
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

---

### Some commands
```bash
# you must first acces to postgres container
docker exec -it mysql bash

# some postgres commands
# 1- connect to a database: mysql -h [hôte] -P [port] -U [utilisateur] -d [nom_base] -p
mysql -h localhost -p 8889 -U nanp -d TYROK -p # password in compose.yml

# 2- Run sql file
# mysql -h [hôte] -P [port] -U [utilisateur] -d [nom_base] -p < /Path/to/your_sql_script.sql
mysql -h localhost -p 8889 -U nanp -d TYROK -p < /Path/to/your_sql_script.sql # password in compose.yml 
```

| **<span style="color:green">Commands</span>** | **<span style="color:green">Description</span>** |
| :--- | :--- | 
| **CREATE DATABASE [db_name]** | `Creer une Base de données.` |
| **DROP DATABASE [db_name]** | `Supprimer une base de données` |
| **SHOW DATABASES** | `Liste les bases de données existantes.` |
| **USE [db_name]** | `travailler dans une base de données spécifique.` |
| **CREATE / ALTER / DROP / TRUNCATE [table]** | `Creer/Modifier/Supprimer/Vider une table spécifique` |
| **SHOW / DESCRIBE [table]** | `Afficher les détails d'une table.` |
| **SELECT / INSERT INTO / UPDATE / DELETE** | `...` |
| **QUIT** | `Quitter.` |

---
