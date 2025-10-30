import os
from dotenv import load_dotenv
from pathlib import Path

# 載入環境變數
load_dotenv()

# 資料庫設定
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "smoking_detection")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# JWT 設定
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 伺服器設定
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))

# AI 模型設定
MODEL_PATH = os.getenv("MODEL_PATH", "GP_v2.pt")

# 偵測設定
DEFAULT_CONFIDENCE = 0.7
DEFAULT_IOU = 0.5

# 檔案儲存
UPLOAD_DIR = Path("uploads")
SCREENSHOT_DIR = Path("screenshots")
UPLOAD_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)
