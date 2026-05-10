
CREATE DATABASE hospital_hci;

USE hospital_hci;

CREATE TABLE user (
id INT AUTO_INCREMENT PRIMARY KEY,
fullname VARCHAR(120),
email VARCHAR(120),
password VARCHAR(255),
role VARCHAR(50),
department VARCHAR(120)
);

CREATE TABLE appointment (
id INT AUTO_INCREMENT PRIMARY KEY,
patient VARCHAR(120),
doctor VARCHAR(120),
appointment_date VARCHAR(120),
status VARCHAR(50)
);

CREATE TABLE payment (
id INT AUTO_INCREMENT PRIMARY KEY,
patient VARCHAR(120),
amount VARCHAR(50),
status VARCHAR(50)
);
