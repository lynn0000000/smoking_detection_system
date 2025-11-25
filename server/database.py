from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, Enum, ForeignKey
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    camera_name = Column(String(100), nullable=False)
    camera_type = Column(String(20), nullable=False)
    camera_source = Column(String(255), nullable=False)
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime)
    api_key = Column(String(64), unique=True)
    
    confidence_threshold = Column(Float, default=0.7)
    iou_threshold = Column(Float, default=0.5)
    enable_alert = Column(Boolean, default=True)
    enable_screenshot = Column(Boolean, default=True)
    nms_threshold = Column(Float, default=0.5)
    draw_bbox = Column(Boolean, default=True)
    detect_mode = Column(Enum('real_time', 'low_power'), default='real_time')
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 關聯
    owner = relationship("User", back_populates="cameras")
    detections = relationship("Detection", back_populates="camera", cascade="all, delete-orphan")


class Detection(Base):
    """偵測記錄表"""
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    
    timestamp = Column(DateTime, default=datetime.now, index=True)
    has_person = Column(Boolean, default=False)
    has_cigarette = Column(Boolean, default=False)
    is_smoking = Column(Boolean, default=False)
    confidence = Column(Float)
    screenshot_path = Column(String(500))
    detection_details = Column(Text)
    
    created_at = Column(DateTime, default=datetime.now)

    # 關聯
    user = relationship("User", back_populates="detections")
    camera = relationship("Camera", back_populates="detections")


class SystemSettings(Base):
    """系統設定表"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    confidence_threshold = Column(Float, default=0.5)
    nms_threshold = Column(Float, default=0.45)
    draw_bbox = Column(Boolean, default=True)
    detect_mode = Column(String(20), default='real_time')
    save_location = Column(String(20), default='server')
    save_days = Column(Integer, default=30)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


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
    init_db()
