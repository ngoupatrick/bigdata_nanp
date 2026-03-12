-- Création de la base de données
CREATE DATABASE IF NOT EXISTS TYROK;
USE TYROK;

-- Attribution des privilèges (Propriétaire de la base TYROK)
-- GRANT ALL PRIVILEGES ON TYROK.* TO 'nanp'@'%';
-- FLUSH PRIVILEGES;

-- Suppression des tables si elles existent (pour repartir de zéro)
-- DROP TABLE IF EXISTS sales;
-- DROP TABLE IF EXISTS product;
-- DROP TABLE IF EXISTS client;

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
