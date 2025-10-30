# 🔧 資料庫初始化問題解決指南

## 問題說明

如果你在執行 `init_database.sql` 時遇到以下錯誤:
```
ERROR 1064 (42000): ParserError: (:) [], ParentContainsErrorRecordException
FullyQualifiedErrorId : RedirectionNotSupported
```

這是因為 **MySQL 8.0+ 對某些字符的處理更嚴格**。

---

## ✅ 解決方案 (3 種方法)

### 🎯 方法 1: 使用 Python 初始化腳本 (推薦)

這是**最簡單且最可靠**的方法！

```bash
# 在專案目錄執行
python setup_database.py
```

這個腳本會自動:
- ✅ 建立資料庫
- ✅ 建立所有資料表
- ✅ 建立測試管理員帳號 (admin/admin123)

---

### 🎯 方法 2: 使用修正版 SQL 檔案

使用我提供的修正版 SQL 檔案:

```bash
mysql -u root -p < init_database_fixed.sql
```

然後使用 API 註冊第一個用戶:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "管理員"
  }'
```

---

### 🎯 方法 3: 手動 SQL 執行

如果你想手動執行,可以在 MySQL 命令列中逐步執行:

```sql
-- 1. 登入 MySQL
mysql -u root -p

-- 2. 建立資料庫
CREATE DATABASE IF NOT EXISTS smoking_detection 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smoking_detection;

-- 3. 建立用戶表
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

-- 4. 建立攝影機表
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

-- 5. 建立偵測記錄表
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

-- 6. 確認表格建立成功
SHOW TABLES;

-- 7. 退出
exit
```

---

## 📋 完整初始化流程 (推薦)

### 步驟 1: 確認 MySQL 正在運行

```bash
# Windows
net start MySQL

# Linux/Mac
sudo systemctl start mysql  # 或 sudo service mysql start
```

### 步驟 2: 設定環境變數

編輯 `.env` 檔案:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password  # ← 改成你的密碼
DB_NAME=smoking_detection
```

### 步驟 3: 安裝 Python 套件

```bash
pip install -r requirements.txt
```

### 步驟 4: 執行 Python 初始化腳本

```bash
python setup_database.py
```

你應該會看到:
```
==============================================================
  🚭 吸菸監控系統 - 資料庫初始化
==============================================================

資料庫設定:
  Host: localhost
  Port: 3306
  User: root
  Database: smoking_detection

步驟 1/3: 建立資料庫...
✅ 資料庫 'smoking_detection' 建立成功

步驟 2/3: 建立資料表...
✅ 資料表建立成功

步驟 3/3: 建立測試管理員...
✅ 測試管理員帳號建立成功
   用戶名: admin
   密碼: admin123
   ⚠️  正式環境請務必修改密碼！

==============================================================
  ✅ 資料庫初始化完成！
==============================================================
```

### 步驟 5: 啟動伺服器

```bash
python -m server.main
```

### 步驟 6: 測試系統

```bash
python test_system.py
```

---

## 🐛 常見問題排查

### Q1: 執行 Python 腳本時出現 "ModuleNotFoundError"

**原因**: 套件沒有安裝

**解決**:
```bash
pip install -r requirements.txt
```

### Q2: MySQL 連線失敗 "Access denied"

**原因**: MySQL 密碼錯誤

**解決**:
1. 檢查 `.env` 中的 `DB_PASSWORD`
2. 確認 MySQL root 密碼

**測試連線**:
```bash
mysql -u root -p
```

### Q3: "Database already exists"

**原因**: 資料庫已經存在

**解決**: 
這不是錯誤！如果要重新初始化:

```sql
-- 刪除舊資料庫
DROP DATABASE IF EXISTS smoking_detection;

-- 重新執行初始化
```

或直接執行:
```bash
python setup_database.py
```
腳本會自動處理。

### Q4: 表格建立成功,但沒有測試用戶

**解決**:
```bash
# 重新執行 Python 腳本
python setup_database.py

# 或透過 API 註冊
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

---

## 🎯 驗證初始化是否成功

### 方法 1: MySQL 命令列

```bash
mysql -u root -p

USE smoking_detection;

-- 查看所有表格
SHOW TABLES;

-- 應該看到:
-- +-----------------------------+
-- | Tables_in_smoking_detection |
-- +-----------------------------+
-- | cameras                     |
-- | detections                  |
-- | users                       |
-- +-----------------------------+

-- 查看用戶
SELECT username, email, is_admin FROM users;

-- 應該看到 admin 用戶

exit
```

### 方法 2: 啟動伺服器測試

```bash
# 啟動伺服器
python -m server.main

# 在另一個終端執行測試
python test_system.py
```

---

## 💡 總結

**最推薦的方式**:
1. 使用 `python setup_database.py` 初始化
2. 使用 `python test_system.py` 測試

**優點**:
- ✅ 簡單快速
- ✅ 自動處理所有細節
- ✅ 不需要手動執行 SQL
- ✅ 自動建立測試帳號

如果還有問題,歡迎隨時詢問! 🚀
