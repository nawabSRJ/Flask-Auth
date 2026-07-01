-- =========================================================
-- USERS 
-- =========================================================

CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(250) NOT NULL, -- stores a hash hence larger limit
    phone VARCHAR(10) UNIQUE NOT NULL, 
    age INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    course VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    photo VARCHAR(255) DEFAULT NULL,
);

-- =========================================================
-- auth_logs 
-- =========================================================

CREATE TABLE auth_logs(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_email VARCHAR(100),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)    
)