CREATE DATABASE IF NOT EXISTS pniot_system;
USE pniot_system;

-- 1. טבלת משתמשים (אדמינים, מנהלים, מהנדסים)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Project Manager', 'Engineer'),
    is_active BOOLEAN DEFAULT FALSE
);

-- 2. טבלת לקוחות (פונים)
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY, -- או מספר ת.ז
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    address VARCHAR(200)
);

-- 3. טבלת פרויקטים
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    division ENUM('רכבות', 'תשתיות', 'אורבני') NOT NULL,
    region VARCHAR(100),
    engineer_id INT,
    FOREIGN KEY (engineer_id) REFERENCES users(id)
);

-- 4. טבלת קישור: מנהלי פרויקטים (רבים לרבים)
CREATE TABLE project_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    manager_id INT,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (manager_id) REFERENCES users(id)
);

-- 5. טבלת פניות
CREATE TABLE inquiries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    project_id INT,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    event_address VARCHAR(200),
    image_path VARCHAR(300),
    status ENUM('חדש', 'בטיפול', 'טופל', 'לא ניתן לביצוע') DEFAULT 'חדש',
    manager_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- יצירת אדמין ראשוני
INSERT INTO users (full_name, email, password, role, is_active) 
VALUES ('System Admin', 'admin@system.com', 'admin123', 'Admin', TRUE);