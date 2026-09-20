CREATE DATABASE IF NOT EXISTS appdb;

USE appdb;

-- Create To-do lists
CREATE TABLE IF NOT EXISTS todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert one initial task
INSERT INTO todos (task) VALUES ( 'Initial task test from MySQL' );