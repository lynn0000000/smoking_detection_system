# 🎨 吸菸監控系統 - 前端界面

## 📋 頁面說明

### 1. login.html - 登入頁面
- 用戶登入
- 記住我功能
- 跳轉註冊頁面

### 2. register.html - 註冊頁面
- 新用戶註冊
- 密碼確認驗證
- 自動跳轉登入

### 3. dashboard.html - 儀表板
- 系統統計資訊
- 7天偵測趨勢圖
- 攝影機狀態圖
- 最近偵測記錄

### 4. cameras.html - 攝影機管理
- 查看所有攝影機
- 新增攝影機
- 取得 API Key
- 刪除攝影機

### 5. detections.html - 偵測記錄
- 查詢所有偵測記錄
- 攝影機篩選
- 狀態篩選
- 查看截圖

---

## 🚀 快速開始

### 方法 1: 直接開啟 (推薦)

由於前端使用純 HTML/CSS/JavaScript,不需要額外安裝:

```bash
# 直接用瀏覽器開啟
start login.html
```

或用 Live Server (VS Code 擴充):
1. 安裝 "Live Server" 擴充
2. 右鍵點擊 `login.html`
3. 選擇 "Open with Live Server"

---

### 方法 2: 使用 Python 簡易伺服器

```bash
# 在 frontend 目錄執行
cd frontend
python -m http.server 8080
```

然後開啟: http://localhost:8080/login.html

---

### 方法 3: 整合到 FastAPI

修改 `server/main_simple.py`,新增靜態檔案服務:

```python
from fastapi.staticfiles import StaticFiles

# 掛載前端檔案
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

然後訪問: http://localhost:8000/login.html

---

## 🔧 設定說明

### API 連線設定

所有頁面的 JavaScript 都有這一行:

```javascript
const API_URL = 'http://localhost:8000';
```

如果你的伺服器在其他位置,請修改這個網址。

---

## 🎯 使用流程

### 1. 註冊帳號
1. 開啟 `register.html`
2. 填寫資料
3. 註冊成功後跳轉登入

### 2. 登入系統
1. 開啟 `login.html`
2. 輸入帳號密碼
3. 勾選"記住我"(選擇性)
4. 登入成功後進入儀表板

### 3. 管理攝影機
1. 點擊側邊欄的"攝影機管理"
2. 點擊"新增攝影機"
3. 填寫攝影機資訊
4. **重要!複製並保存 API Key**
5. 在攝影機端使用該 API Key 連線

### 4. 查看偵測記錄
1. 點擊"偵測記錄"
2. 可以篩選特定攝影機
3. 可以只顯示有吸菸的記錄
4. 點擊"查看"可以看截圖(功能開發中)

---

## 📱 功能特色

### ✅ 已實現
- 用戶認證 (JWT Token)
- 響應式設計 (手機/平板適配)
- 即時數據更新
- 圖表視覺化 (Chart.js)
- 攝影機CRUD操作
- 偵測記錄查詢
- 美觀的UI設計

### 🚧 待開發
- 即時影像監控
- 截圖查看器
- 攝影機編輯功能
- 匯出報表功能
- 即時警報通知
- 多語言支援

---

## 🎨 技術棧

- **HTML5** - 網頁結構
- **CSS3** - 樣式設計
- **Bootstrap 5** - UI 框架
- **Bootstrap Icons** - 圖標
- **JavaScript (原生)** - 功能邏輯
- **Chart.js** - 圖表庫
- **Fetch API** - HTTP 請求

---

## 🔐 安全性

- JWT Token 認證
- LocalStorage/SessionStorage 儲存
- "記住我"功能
- 自動登出保護

---

## 📝 注意事項

1. **CORS 設定**: 確保後端 API 已設定 CORS
2. **API Key 保密**: 不要將 API Key 提交到 Git
3. **瀏覽器支援**: 建議使用 Chrome, Firefox, Edge 最新版
4. **伺服器運行**: 使用前端前請確保後端 API 正在運行

---

## 🐛 常見問題

### Q1: 無法登入
**解決**: 
- 確認後端伺服器正在運行
- 檢查 API_URL 設定
- 查看瀏覽器 Console 錯誤訊息

### Q2: CORS 錯誤
**解決**:
確認 `server/main.py` 有以下設定:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q3: 圖表不顯示
**解決**:
- 確認網路連線 (Chart.js 從 CDN 載入)
- 檢查瀏覽器 Console

---

## 📞 支援

如有問題,請檢查:
1. 瀏覽器 Console (F12)
2. 後端伺服器日誌
3. 網路請求 (F12 → Network tab)

---

## 🎉 完成!

你的前端界面已經完成!

**下一步**:
1. 測試所有功能
2. 自訂樣式和配色
3. 新增更多功能
4. 準備專題展示

祝使用愉快! 🚀