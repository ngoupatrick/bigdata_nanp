
-- 1. Droits de réplication pour MySQL 8.0 (Indispensable pour Debezium)
GRANT ALL PRIVILEGES ON *.* TO 'nanp'@'%';
-- GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'nanp'@'%';
FLUSH PRIVILEGES;
