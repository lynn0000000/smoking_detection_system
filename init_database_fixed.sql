-- 吸菸監控系統 - MySQL 資料庫初始化腳本 (修正版)

-- 建立資料庫
CREATE DATABASE IF NOT EXISTS smoking_detection CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smoking_detection;

-- 用戶表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 攝影機表
CREATE TABLE IF NOT EXISTS cameras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    camera_name VARCHAR(100) NOT NULL,
    camera_type VARCHAR(20) NOT NULL,
    camera_source VARCHAR(255) NOT NULL,
    location VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    is_online BOOLEAN DEFAULT FALSE,
    last_seen DATETIME,
    api_key VARCHAR(64) NOT NULL UNIQUE,
    confidence_threshold FLOAT DEFAULT 0.7,
    iou_threshold FLOAT DEFAULT 0.5,
    enable_alert BOOLEAN DEFAULT TRUE,
    enable_screenshot BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_api_key (api_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 偵測記錄表
CREATE TABLE IF NOT EXISTS detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    camera_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    has_person BOOLEAN DEFAULT FALSE,
    has_cigarette BOOLEAN DEFAULT FALSE,
    is_smoking BOOLEAN DEFAULT FALSE,
    confidence FLOAT,
    screenshot_path VARCHAR(500),
    detection_details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_camera_id (camera_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_is_smoking (is_smoking)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 顯示建立完成訊息
SELECT '資料庫初始化完成！' AS message;
SELECT '請透過 API 註冊用戶' AS info;
