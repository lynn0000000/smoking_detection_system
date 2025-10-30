from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from server.config import DATABASE_URL

# 建立資料庫引擎
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== 資料表定義 ====================

class User(Base):
    """用戶表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 關聯
    cameras = relationship("Camera", back_populates="owner", cascade="all, delete-orphan")
    detections = relationship("Detection", back_populates="user", cascade="all, delete-orphan")


class Camera(Base):
    """攝影機表"""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    camera_name = Column(String(100), nullable=False)
    camera_type = Column(String(20), nullable=False)  # 'local', 'rtsp', 'usb'
    camera_source = Column(String(255), nullable=False)  # 0, 1, rtsp://..., http://...
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime)
    api_key = Column(String(64), unique=True, index=True)  # 攝影機連線用的API Key
    
    # 設定
    confidence_threshold = Column(Float, default=0.7)
    iou_threshold = Column(Float, default=0.5)
    enable_alert = Column(Boolean, default=True)
    enable_screenshot = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 關聯
    owner = relationship("User", back_populates="cameras")
    detections = relationship("Detection", back_populates="camera", cascade="all, delete-orphan")


class Detection(Base):
    """偵測記錄表"""
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    
    # 偵測資訊
    timestamp = Column(DateTime, default=datetime.now, index=True)
    has_person = Column(Boolean, default=False)
    has_cigarette = Column(Boolean, default=False)
    is_smoking = Column(Boolean, default=False)
    confidence = Column(Float)
    
    # 截圖
    screenshot_path = Column(String(500))
    
    # 偵測詳情 (JSON格式儲存所有框的資訊)
    detection_details = Column(Text)  # JSON字串
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 關聯
    user = relationship("User", back_populates="detections")
    camera = relationship("Camera", back_populates="detections")


# ==================== 資料庫操作函數 ====================

def init_db():
    """初始化資料庫(建立所有表)"""
    Base.metadata.create_all(bind=engine)
    print("✅ 資料庫表建立完成")


def get_db():
    """取得資料庫 session (用於 FastAPI 依賴注入)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """強制重建所有表 (開發用)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ 資料庫表重建完成")


if __name__ == "__main__":
    # 測試用:建立資料庫表
    init_db()
