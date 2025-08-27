-- NutriTame MySQL Database Setup
-- Run this in your Hostinger MySQL database

-- Users table (replaces MongoDB users collection)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    subscription_tier ENUM('basic', 'premium') DEFAULT 'premium',
    subscription_status ENUM('trial', 'active', 'inactive', 'canceled') DEFAULT 'active',
    trial_end_date DATETIME,
    subscription_end_date DATETIME,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Profile fields
    diabetes_type ENUM('type1', 'type2', 'prediabetes'),
    age INT,
    gender ENUM('male', 'female', 'other', 'prefer_not_to_say'),
    activity_level ENUM('low', 'moderate', 'high'),
    health_goals JSON,
    food_preferences JSON,
    cultural_background VARCHAR(255),
    allergies JSON,
    dislikes JSON,
    cooking_skill ENUM('beginner', 'intermediate', 'advanced'),
    phone_number VARCHAR(20),
    
    -- SaaS fields
    tenant_id VARCHAR(36),
    is_demo_user BOOLEAN DEFAULT FALSE,
    
    INDEX idx_email (email),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_demo_user (is_demo_user)
);

-- Chat sessions table (replaces MongoDB chat_sessions collection)
CREATE TABLE IF NOT EXISTS chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(36),
    title VARCHAR(255),
    messages JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_tenant_id (tenant_id)
);

-- Chat messages table (replaces MongoDB chat_messages collection)
CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp)
);

-- Restaurants table (cached restaurant data)
CREATE TABLE IF NOT EXISTS restaurants (
    id VARCHAR(36) PRIMARY KEY,
    place_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    rating DECIMAL(2, 1),
    price_level INT,
    phone_number VARCHAR(20),
    website VARCHAR(500),
    opening_hours JSON,
    photos JSON,
    cuisine_types JSON,
    diabetic_friendly_score DECIMAL(2, 1),
    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_place_id (place_id),
    INDEX idx_location (latitude, longitude)
);

-- Nutrition data table (cached USDA data)
CREATE TABLE IF NOT EXISTS nutrition_data (
    id VARCHAR(36) PRIMARY KEY,
    fdc_id VARCHAR(20) UNIQUE NOT NULL,
    food_name VARCHAR(255) NOT NULL,
    description TEXT,
    brand_name VARCHAR(255),
    serving_size VARCHAR(100),
    calories DECIMAL(6, 2),
    carbohydrates DECIMAL(6, 2),
    sugars DECIMAL(6, 2),
    fiber DECIMAL(6, 2),
    protein DECIMAL(6, 2),
    fat DECIMAL(6, 2),
    sodium DECIMAL(6, 2),
    diabetic_rating ENUM('excellent', 'good', 'moderate', 'caution'),
    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_fdc_id (fdc_id),
    INDEX idx_food_name (food_name)
);

-- Shopping lists table
CREATE TABLE IF NOT EXISTS shopping_lists (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    items JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

-- Payment transactions table
CREATE TABLE IF NOT EXISTS payment_transactions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    stripe_session_id VARCHAR(255),
    amount DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    plan_type ENUM('basic', 'premium'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_stripe_session_id (stripe_session_id)
);

-- Admin users table
CREATE TABLE IF NOT EXISTS admin_users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'super_admin') DEFAULT 'admin',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_email (email)
);

-- API usage tracking table
CREATE TABLE IF NOT EXISTS api_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_name VARCHAR(100) NOT NULL,
    calls_made INT DEFAULT 0,
    month_year VARCHAR(7) NOT NULL, -- Format: 'YYYY-MM'
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_api_month (api_name, month_year),
    INDEX idx_month_year (month_year)
);

-- Insert default admin user (change password!)
INSERT IGNORE INTO admin_users (id, email, password_hash, role) VALUES (
    'admin-001', 
    'admin@nutritame.com', 
    '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- password: 'password'
    'super_admin'
);

-- Insert default API usage tracking
INSERT IGNORE INTO api_usage (api_name, calls_made, month_year) VALUES 
('google-places', 0, DATE_FORMAT(NOW(), '%Y-%m')),
('usda-nutrition', 0, DATE_FORMAT(NOW(), '%Y-%m'));