# 🚭 吸菸監控系統 v2.0

多用戶、多攝影機的智能吸菸偵測系統，支援 USB 攝影機、RTSP 串流（小米監視器等）。

## 📋 功能特色

- ✅ **多用戶管理**: JWT 認證、用戶註冊/登入
- ✅ **多攝影機支援**: 每個用戶可管理多個攝影機
- ✅ **多種來源**: USB攝影機、RTSP串流、網路攝影機
- ✅ **AI 偵測**: YOLOv8 實時吸菸行為偵測
- ✅ **自動截圖**: 偵測到吸菸時自動儲存證據
- ✅ **記錄查詢**: 完整的偵測歷史記錄
- ✅ **統計分析**: 偵測統計、攝影機狀態監控

## 🏗️ 系統架構

```
客戶端 (攝影機)  →  WebSocket  →  伺服器 (FastAPI)  →  AI 偵測  →  MySQL 資料庫
     ↑                                    ↓
  USB / RTSP                          截圖 + 警報
```

## 📦 安裝步驟

### 1. 環境需求

- Python 3.8+
- MySQL 8.0+
- (可選) CUDA 支援的 GPU

### 2. 安裝 MySQL

**Windows:**
```bash
# 下載並安裝 MySQL: https://dev.mysql.com/downloads/installer/
# 設定 root 密碼
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### 3. 初始化資料庫

```bash
# 登入 MySQL
mysql -u root -p

# 執行初始化腳本
source init_database.sql

# 或直接執行
mysql -u root -p < init_database.sql
```

### 4. 安裝 Python 套件

```bash
# 安裝依賴
pip install -r requirements.txt

# 如果需要 GPU 支援
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 5. 設定環境變數

編輯 `.env` 檔案:

```env
# 資料庫設定
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=smoking_detection

# JWT 設定 (請修改為隨機字串)
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI 模型
MODEL_PATH=GP_v2.pt
```

### 6. 放置 AI 模型

將 `GP_v2.pt` 放在專案根目錄

## 🚀 使用方法

### 啟動伺服器

```bash
cd smoking_detection_system
python -m server.main

# 或使用 uvicorn
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

伺服器啟動後，訪問: http://localhost:8000

### 註冊帳號與設定攝影機

#### 1. 註冊用戶

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user123",
    "email": "user@example.com",
    "password": "password123",
    "full_name": "測試用戶"
  }'
```

#### 2. 登入取得 Token

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user123",
    "password": "password123"
  }'
```

回應:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**記住這個 `access_token`，後續 API 都需要!**

#### 3. 新增攝影機

```bash
curl -X POST "http://localhost:8000/api/cameras" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "camera_name": "客廳監視器",
    "camera_type": "rtsp",
    "camera_source": "rtsp://admin:password@192.168.1.100:554/stream1",
    "location": "1F 客廳"
  }'
```

回應:
```json
{
  "id": 1,
  "camera_name": "客廳監視器",
  "api_key": "xyz123abc456...",
  "message": "攝影機新增成功,請妥善保管 API Key"
}
```

**記住這個 `api_key`，客戶端連線需要!**

### 啟動客戶端 (攝影機端)

#### 範例 1: USB 攝影機

```bash
cd smoking_detection_system
python client/camera_client.py \
  --server ws://localhost:8000 \
  --api-key YOUR_API_KEY \
  --type usb \
  --source 0
```

#### 範例 2: 小米監視器 (RTSP)

```bash
python client/camera_client.py \
  --server ws://localhost:8000 \
  --api-key YOUR_API_KEY \
  --type rtsp \
  --source "rtsp://admin:password@192.168.1.100:554/stream1"
```

#### 範例 3: 本地攝影機

```bash
python client/camera_client.py \
  --server ws://localhost:8000 \
  --api-key YOUR_API_KEY \
  --type local \
  --source 0
```

### 查詢偵測記錄

```bash
curl -X GET "http://localhost:8000/api/detections?limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 查看統計資料

```bash
curl -X GET "http://localhost:8000/api/statistics" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📱 小米監視器 RTSP 設定

### 取得 RTSP 串流網址

1. 開啟小米攝影機 App
2. 進入攝影機設定
3. 找到「RTSP」或「串流」設定
4. 啟用 RTSP
5. 記下 RTSP URL 格式:
   ```
   rtsp://[用戶名]:[密碼]@[IP地址]:[端口]/[路徑]
   ```

### 常見小米監視器 RTSP 格式

```bash
# 一般格式
rtsp://admin:password@192.168.1.100:554/stream1

# 高清串流
rtsp://admin:password@192.168.1.100:554/stream1

# 低清串流 (省頻寬)
rtsp://admin:password@192.168.1.100:554/stream2
```

### 測試 RTSP 連線

使用 VLC 播放器測試:
```
媒體 → 開啟網路串流 → 輸入 RTSP URL → 播放
```

## 🔧 API 文件

啟動伺服器後訪問自動生成的 API 文件:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📂 專案結構

```
smoking_detection_system/
├── server/                    # 伺服器端
│   ├── main.py               # 主程式 (FastAPI)
│   ├── database.py           # 資料庫模型 (SQLAlchemy)
│   ├── auth.py               # 認證系統 (JWT)
│   └── config.py             # 設定檔
├── client/                    # 客戶端
│   └── camera_client.py      # 攝影機客戶端程式
├── screenshots/               # 截圖儲存目錄
├── init_database.sql          # 資料庫初始化腳本
├── requirements.txt           # Python 依賴
├── .env                       # 環境變數設定
├── GP_v2.pt                   # AI 模型 (請自行放置)
└── README.md                  # 說明文件
```

## 🎯 使用流程

```
1. 啟動 MySQL 資料庫
2. 執行資料庫初始化腳本
3. 啟動 FastAPI 伺服器
4. 註冊用戶並登入
5. 新增攝影機 (取得 API Key)
6. 在攝影機端執行客戶端程式
7. 查看偵測記錄和統計
```

## ⚙️ 進階設定

### 修改偵測參數

更新攝影機設定:
```bash
curl -X PUT "http://localhost:8000/api/cameras/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "confidence_threshold": 0.8,
    "iou_threshold": 0.6,
    "enable_alert": true,
    "enable_screenshot": true
  }'
```

### 遠端部署

如果伺服器在其他電腦:

```bash
# 客戶端連線到遠端伺服器
python client/camera_client.py \
  --server ws://192.168.1.100:8000 \
  --api-key YOUR_API_KEY \
  --type rtsp \
  --source "rtsp://..."
```

### 防火牆設定

開放端口 8000:
```bash
# Linux
sudo ufw allow 8000

# Windows
# 控制台 → Windows Defender 防火牆 → 進階設定 → 輸入規則 → 新增規則
```

## 🐛 常見問題

### Q1: 連線失敗 "無效的 API Key"
- 檢查 API Key 是否正確
- 確認攝影機已在網頁中註冊

### Q2: RTSP 串流無法連線
- 確認監視器已開啟 RTSP 功能
- 檢查用戶名、密碼、IP 是否正確
- 使用 VLC 測試串流是否正常

### Q3: MySQL 連線失敗
- 檢查 `.env` 中的資料庫設定
- 確認 MySQL 服務已啟動
- 檢查防火牆設定

### Q4: GPU 不可用
- 安裝 CUDA 版本的 PyTorch
- 確認 NVIDIA 驅動已安裝
- 系統會自動降級使用 CPU

## 📊 資料庫管理

### 備份資料庫

```bash
mysqldump -u root -p smoking_detection > backup.sql
```

### 還原資料庫

```bash
mysql -u root -p smoking_detection < backup.sql
```

### 清空偵測記錄

```sql
USE smoking_detection;
DELETE FROM detections WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

## 📝 測試帳號

預設管理員帳號 (請在正式環境中刪除):
- 用戶名: `admin`
- 密碼: `admin123`

## 🔐 安全建議

1. 修改 `.env` 中的 `SECRET_KEY` 為隨機字串
2. 使用強密碼
3. 定期更新 API Key
4. 啟用 HTTPS (生產環境)
5. 設定資料庫訪問權限

## 📞 技術支援

- 問題回報: [GitHub Issues]
- 文件: http://localhost:8000/docs

## 📄 授權

MIT License

---

**注意事項:**
- 請確保符合當地法律法規使用監控系統
- 建議在公共場所使用時設置明顯告示
- 定期檢查系統日誌和偵測準確度
