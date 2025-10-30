# 🚀 快速啟動指南

## 30 秒快速開始

### 步驟 1: 啟動資料庫
```bash
# 確認 MySQL 已啟動
mysql -u root -p

# 執行初始化
source init_database.sql
# 或
mysql -u root -p < init_database.sql
```

### 步驟 2: 設定環境
```bash
# 編輯 .env 檔案，修改資料庫密碼
nano .env

# 確認 GP_v2.pt 模型檔案存在
ls GP_v2.pt
```

### 步驟 3: 安裝套件
```bash
pip install -r requirements.txt
```

### 步驟 4: 啟動伺服器
```bash
python -m server.main
# 或
uvicorn server.main:app --reload
```

### 步驟 5: 測試系統
```bash
# 在新終端執行
python test_system.py
```

### 步驟 6: 啟動攝影機客戶端
```bash
# 使用測試腳本輸出的指令
python client/camera_client.py \
  --server ws://localhost:8000 \
  --api-key YOUR_API_KEY \
  --type usb \
  --source 0
```

---

## 🎯 完整流程

### 1️⃣ 資料庫設定

```bash
# 登入 MySQL
mysql -u root -p

# 執行初始化腳本
source init_database.sql

# 退出
exit
```

### 2️⃣ 環境設定

編輯 `.env`:
```env
DB_PASSWORD=your_mysql_password
SECRET_KEY=your-random-secret-key-here
MODEL_PATH=GP_v2.pt
```

### 3️⃣ 啟動伺服器

```bash
# 方法 1: 直接執行
python -m server.main

# 方法 2: 使用 uvicorn (開發模式)
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

# 方法 3: 使用 uvicorn (生產模式)
uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 4
```

訪問: http://localhost:8000

### 4️⃣ 註冊用戶 (3 種方法)

**方法 1: 使用測試腳本**
```bash
python test_system.py
```

**方法 2: 使用 curl**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "email": "myuser@example.com",
    "password": "mypassword123",
    "full_name": "我的名字"
  }'
```

**方法 3: 使用 Swagger UI**
- 訪問: http://localhost:8000/docs
- 找到 `/api/auth/register`
- 點擊 "Try it out"
- 填寫資料並執行

### 5️⃣ 登入取得 Token

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "mypassword123"
  }'
```

回應會包含 `access_token`，複製它！

### 6️⃣ 新增攝影機

```bash
# 替換 YOUR_TOKEN
curl -X POST "http://localhost:8000/api/cameras" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "camera_name": "我的攝影機",
    "camera_type": "usb",
    "camera_source": "0",
    "location": "客廳"
  }'
```

回應會包含 `api_key`，複製它！

### 7️⃣ 啟動客戶端

**USB 攝影機:**
```bash
python client/camera_client.py \
  --server ws://localhost:8000 \
  --api-key YOUR_API_KEY \
  --type usb \
  --source 0
```

**小米監視器 (RTSP):**
```bash
python client/camera_client.py \
  --server ws://localhost:8000 \
  --api-key YOUR_API_KEY \
  --type rtsp \
  --source "rtsp://admin:password@192.168.1.100:554/stream1"
```

### 8️⃣ 查看偵測記錄

```bash
curl -X GET "http://localhost:8000/api/detections?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔧 常用指令

### 查看攝影機列表
```bash
curl -X GET "http://localhost:8000/api/cameras" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 查看統計資料
```bash
curl -X GET "http://localhost:8000/api/statistics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 更新攝影機設定
```bash
curl -X PUT "http://localhost:8000/api/cameras/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "confidence_threshold": 0.8,
    "enable_screenshot": true
  }'
```

### 刪除攝影機
```bash
curl -X DELETE "http://localhost:8000/api/cameras/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📋 檢查清單

啟動前確認:
- [ ] MySQL 已安裝並運行
- [ ] 資料庫已初始化 (`init_database.sql`)
- [ ] `.env` 檔案已設定
- [ ] `GP_v2.pt` 模型檔案存在
- [ ] Python 套件已安裝 (`pip install -r requirements.txt`)

---

## 🐛 問題排查

### 伺服器無法啟動
```bash
# 檢查端口是否被占用
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# 使用其他端口
uvicorn server.main:app --port 8001
```

### 資料庫連線失敗
```bash
# 測試 MySQL 連線
mysql -u root -p -h localhost

# 檢查 .env 設定
cat .env | grep DB_
```

### 攝影機連線失敗
```bash
# 檢查 API Key 是否正確
# 確認伺服器正在運行
# 查看伺服器日誌

# 測試網路連線
ping localhost
```

### RTSP 串流無法連線
```bash
# 使用 VLC 測試
# 媒體 → 開啟網路串流 → 輸入 RTSP URL

# 使用 ffplay 測試
ffplay rtsp://admin:password@192.168.1.100:554/stream1
```

---

## 🎓 學習資源

- API 文件: http://localhost:8000/docs
- 完整說明: [README.md](README.md)
- 資料庫結構: [init_database.sql](init_database.sql)

---

## 💡 小技巧

1. **開發模式**: 使用 `--reload` 自動重載
2. **多終端**: 伺服器和客戶端分別在不同終端運行
3. **日誌查看**: 伺服器日誌會顯示所有連線和偵測
4. **Swagger UI**: 最方便的 API 測試工具
5. **測試帳號**: `admin` / `admin123` (記得刪除)

---

**祝使用愉快！** 🚀
