-- ========================================================
-- Holiday Hacker Database Schema
-- ========================================================

CREATE DATABASE IF NOT EXISTS holiday_hacker;
USE holiday_hacker;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    available_leaves INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Public Holidays Table
CREATE TABLE IF NOT EXISTS public_holidays (
    id INT AUTO_INCREMENT PRIMARY KEY,
    holiday_name VARCHAR(150) NOT NULL,
    holiday_date DATE NOT NULL,
    description TEXT
);

-- 3. User Leaves Table
CREATE TABLE IF NOT EXISTS user_leaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    leave_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'approved',
    CONSTRAINT fk_user_leaves_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_user_leave UNIQUE (user_id, leave_date)
);

-- 4. Holiday Plans Table
CREATE TABLE IF NOT EXISTS holiday_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    plan_name VARCHAR(150) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    leaves_used INT NOT NULL,
    consecutive_days INT NOT NULL,
    efficiency DOUBLE NOT NULL,
    recommended_dates TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_holiday_plans_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ========================================================
-- Sample Initial Data (Optional)
-- ========================================================

-- Default Test User: username/email='testuser', password='test123'
INSERT IGNORE INTO users (id, name, email, password_hash, role, available_leaves) 
VALUES (1, 'Test User', 'testuser', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', 'user', 10);

-- Default Admin User: username/email='admin', password='adminpassword' (SHA-256)
INSERT IGNORE INTO users (id, name, email, password_hash, role, available_leaves) 
VALUES (2, 'System Admin', 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', 20);

-- Sample Public Holidays (2026)
INSERT IGNORE INTO public_holidays (holiday_name, holiday_date, description) VALUES
('New Year\'s Day', '2026-01-01', 'First day of the year'),
('Republic Day', '2026-01-26', 'Republic Day of India'),
('Maha Shivratri', '2026-02-17', 'Festival of Shiva'),
('Holi', '2026-03-04', 'Festival of Colors'),
('Good Friday', '2026-04-03', 'Christian Holiday'),
('Eid al-Fitr', '2026-04-20', 'Islamic Holiday'),
('Independence Day', '2026-08-15', 'National Independence Day'),
('Gandhi Jayanti', '2026-10-02', 'Mahatma Gandhi Birthday'),
('Dussehra', '2026-10-20', 'Vijayadashami'),
('Diwali', '2026-11-08', 'Festival of Lights'),
('Christmas Day', '2026-12-25', 'Christmas Celebration');
