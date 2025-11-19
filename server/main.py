# ==================== 路徑修正 ====================
import sys
from pathlib import Path



# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ==================== 標準函式庫 ====================
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime, timedelta
import asyncio
import json
import base64
from pathlib import Path
from typing import List, Optional
import torch
# ==================== 專案模組 ====================
from server.database import get_db, User, Camera, Detection, init_db
from server.auth import (
    authenticate_user, create_access_token, get_current_user, 
    get_password_hash, UserCreate, UserLogin, Token, UserResponse,
    generate_camera_api_key, verify_camera_api_key
)
from server.config import MODEL_PATH, SCREENSHOT_DIR
from pydantic import BaseModel

# ==================== FastAPI 應用程式 ====================
app = FastAPI(title="吸菸監控系統 API v2", version="2.0")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全域變數
model = None
active_websockets = {}  # {camera_id: [websocket1, websocket2, ...]}
# 全域變數
last_detection_time = {}  # {camera_id: datetime}
DETECTION_COOLDOWN = timedelta(seconds=10)  # 同一攝影機10秒內只記一次
DETECTION_STABLE_FRAMES = 3  # 連續3幀偵測到才算真正吸菸
smoking_frame_counter = {}  # {camera_id: 目前連續吸菸幀數}
from fastapi.staticfiles import StaticFiles
import os

# 假設你的 frontend 資料夾和 main.py 是同層，路徑就用 "frontend"
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ==================== Pydantic 模型 ====================

class CameraCreate(BaseModel):
    camera_name: str
    camera_type: str  # 'local', 'rtsp', 'usb'
    camera_source: str  # "0", "rtsp://...", etc.
    location: Optional[str] = None


class CameraUpdate(BaseModel):
    camera_name: Optional[str] = None
    location: Optional[str] = None
    confidence_threshold: Optional[float] = None
    iou_threshold: Optional[float] = None
    enable_alert: Optional[bool] = None
    enable_screenshot: Optional[bool] = None


class DetectionResponse(BaseModel):
    id: int
    timestamp: datetime
    camera_name: str
    location: Optional[str]
    has_person: bool
    has_cigarette: bool
    is_smoking: bool
    confidence: float
    screenshot_path: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== 初始化 ====================

def init_model():
    """初始化 YOLO 模型"""
    global model
    try:
        model = YOLO(MODEL_PATH)
        
        if torch.cuda.is_available():
            print(f"✅ 使用 GPU: {torch.cuda.get_device_name(0)}")
            model.to('cuda')
        else:
            print("⚠️ GPU 不可用，使用 CPU")
        
        print("✅ 模型載入成功")
    except Exception as e:
        print(f"❌ 模型載入失敗: {e}")


# def init_model():
#     """初始化 YOLO 模型"""
#     global model
#     print("⚠️ AI 模型暫時停用")
#     model = None

@app.on_event("startup")
async def startup_event():
    """啟動時初始化"""
    init_db()
    init_model()
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    print("✅ 系統初始化完成")


# ==================== 認證 API ====================

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用戶註冊"""
    # 檢查用戶名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用戶名已被使用")
    
    # 檢查 email 是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email 已被使用")
    
    # 建立新用戶
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.post("/api/auth/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """用戶登入"""
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 建立 access token
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """取得當前用戶資訊"""
    return current_user


# ==================== 攝影機管理 API ====================

@app.post("/api/cameras")
async def create_camera(
    camera: CameraCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新增攝影機"""
    api_key = generate_camera_api_key()
    
    db_camera = Camera(
        user_id=current_user.id,
        camera_name=camera.camera_name,
        camera_type=camera.camera_type,
        camera_source=camera.camera_source,
        location=camera.location,
        api_key=api_key
    )
    
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    
    return {
        "id": db_camera.id,
        "camera_name": db_camera.camera_name,
        "api_key": api_key,
        "message": "攝影機新增成功,請妥善保管 API Key"
    }


@app.get("/api/cameras")
async def list_cameras(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """列出用戶的所有攝影機"""
    cameras = db.query(Camera).filter(Camera.user_id == current_user.id).all()
    return cameras


@app.get("/api/cameras/{camera_id}")
async def get_camera(
    camera_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取得攝影機詳細資訊"""
    camera = db.query(Camera).filter(
        Camera.id == camera_id,
        Camera.user_id == current_user.id
    ).first()
    
    if not camera:
        raise HTTPException(status_code=404, detail="攝影機不存在")
    
    return camera


@app.put("/api/cameras/{camera_id}")
async def update_camera(
    camera_id: int,
    camera_update: CameraUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新攝影機設定"""
    camera = db.query(Camera).filter(
        Camera.id == camera_id,
        Camera.user_id == current_user.id
    ).first()
    
    if not camera:
        raise HTTPException(status_code=404, detail="攝影機不存在")
    
    # 更新欄位
    update_data = camera_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(camera, key, value)
    
    db.commit()
    db.refresh(camera)
    
    return {"message": "攝影機設定已更新", "camera": camera}


@app.delete("/api/cameras/{camera_id}")
async def delete_camera(
    camera_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """刪除攝影機"""
    camera = db.query(Camera).filter(
        Camera.id == camera_id,
        Camera.user_id == current_user.id
    ).first()
    
    if not camera:
        raise HTTPException(status_code=404, detail="攝影機不存在")
    
    db.delete(camera)
    db.commit()
    
    return {"message": "攝影機已刪除"}


# ==================== 偵測記錄 API ====================

from datetime import datetime, timedelta
from typing import Optional

@app.get("/api/detections")
async def get_detections(
    camera_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取得偵測記錄（可依攝影機 & 日期區間篩選）"""

    query = db.query(Detection).filter(Detection.user_id == current_user.id)
    
    # 攝影機篩選
    if camera_id:
        query = query.filter(Detection.camera_id == camera_id)

    # 日期處理（格式 YYYY-MM-DD）
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Detection.timestamp >= start)
        except:
            raise HTTPException(status_code=400, detail="start_date 格式錯誤，需為 YYYY-MM-DD")

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Detection.timestamp < end)
        except:
            raise HTTPException(status_code=400, detail="end_date 格式錯誤，需為 YYYY-MM-DD")

    # 排序 + 限制
    detections = query.order_by(Detection.timestamp.desc()).limit(limit).all()
    
    # 加入攝影機名稱
    result = []
    for d in detections:
        camera = db.query(Camera).filter(Camera.id == d.camera_id).first()
        result.append({
            "id": d.id,
            "timestamp": d.timestamp,
            "camera_name": camera.camera_name if camera else "未知",
            "location": camera.location if camera else None,
            "has_person": d.has_person,
            "has_cigarette": d.has_cigarette,
            "is_smoking": d.is_smoking,
            "confidence": d.confidence,
            "screenshot_path": d.screenshot_path
        })
    
    return result



@app.get("/api/statistics")
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取得統計資料"""
    # 總偵測數
    total = db.query(Detection).filter(Detection.user_id == current_user.id).count()
    
    # 今日偵測數
    today = datetime.now().date()
    today_count = db.query(Detection).filter(
        Detection.user_id == current_user.id,
        Detection.timestamp >= today
    ).count()
    
    # 攝影機數量
    camera_count = db.query(Camera).filter(Camera.user_id == current_user.id).count()
    
    # 在線攝影機數
    online_cameras = db.query(Camera).filter(
        Camera.user_id == current_user.id,
        Camera.is_online == True
    ).count()
    
    return {
        "total_detections": total,
        "today_detections": today_count,
        "total_cameras": camera_count,
        "online_cameras": online_cameras
    }



from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

@app.get("/api/detections/trend")
async def get_detection_trend(
    days: int = 7,  # 預設顯示7天
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取得偵測趨勢數據"""
    try:
        # 計算日期範圍
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)  # 包含今天
        
        # 查詢每天的偵測數量
        # 使用 SQLAlchemy 的 func 來做日期分組
        from sqlalchemy import func, cast, Date
        
        daily_counts = db.query(
            cast(Detection.timestamp, Date).label('date'),
            func.count(Detection.id).label('count')
        ).filter(
            Detection.user_id == current_user.id,
            Detection.timestamp >= start_date,
            Detection.timestamp <= end_date
        ).group_by(
            cast(Detection.timestamp, Date)
        ).all()
        
        # 建立日期到數量的映射
        date_count_map = {
            count.date.strftime('%Y-%m-%d'): count.count 
            for count in daily_counts
        }
        
        # 生成連續的日期序列（包含沒有偵測的日期）
        dates = []
        counts = []
        current = start_date.date()
        end = end_date.date()
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            dates.append(date_str)
            counts.append(date_count_map.get(date_str, 0))
            current += timedelta(days=1)
        
        # 如果需要，也可以加入吸菸偵測的統計
        smoking_counts = db.query(
            cast(Detection.timestamp, Date).label('date'),
            func.count(Detection.id).label('count')
        ).filter(
            Detection.user_id == current_user.id,
            Detection.timestamp >= start_date,
            Detection.timestamp <= end_date,
            Detection.is_smoking == True  # 只統計吸菸偵測
        ).group_by(
            cast(Detection.timestamp, Date)
        ).all()
        
        smoking_count_map = {
            count.date.strftime('%Y-%m-%d'): count.count 
            for count in smoking_counts
        }
        
        smoking_data = []
        current = start_date.date()
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            smoking_data.append(smoking_count_map.get(date_str, 0))
            current += timedelta(days=1)
        
        return {
            "success": True,
            "dates": dates,
            "counts": counts,
            "smoking_counts": smoking_data,  # 吸菸偵測數據
            "days": days
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 選擇性：新增每小時趨勢 API（顯示今天的24小時趨勢）
@app.get("/api/detections/hourly-trend")
async def get_hourly_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取得今日每小時的偵測趨勢"""
    try:
        from sqlalchemy import func, extract
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        hourly_counts = db.query(
            extract('hour', Detection.timestamp).label('hour'),
            func.count(Detection.id).label('count')
        ).filter(
            Detection.user_id == current_user.id,
            Detection.timestamp >= today,
            Detection.timestamp < tomorrow
        ).group_by(
            extract('hour', Detection.timestamp)
        ).all()
        
        # 建立小時映射
        hour_count_map = {int(count.hour): count.count for count in hourly_counts}
        
        # 生成24小時數據
        hours = list(range(24))
        counts = [hour_count_map.get(hour, 0) for hour in hours]
        labels = [f"{hour:02d}:00" for hour in hours]
        
        return {
            "success": True,
            "labels": labels,
            "counts": counts
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
# ==================== WebSocket 即時串流 (客戶端上傳) ====================

@app.websocket("/ws/upload/{api_key}")
async def websocket_upload(websocket: WebSocket, api_key: str, db: Session = Depends(get_db)):
    """接收客戶端攝影機上傳的影像並進行偵測"""
    await websocket.accept()
    
    # 驗證 API Key
    try:
        camera = verify_camera_api_key(api_key, db)
    except HTTPException:
        await websocket.close(code=1008, reason="無效的 API Key")
        return
    
    # 更新攝影機狀態
    camera.is_online = True
    camera.last_seen = datetime.now()
    db.commit()
    
    print(f"📷 攝影機 [{camera.camera_name}] 已連線")
    
    try:
        while True:
            # 接收 base64 編碼的影像
            data = await websocket.receive_json()
            
            if data.get("type") == "frame":
                frame_base64 = data.get("data")
                
                # 解碼影像
                img_data = base64.b64decode(frame_base64)
                np_arr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                # 執行偵測
                detection_data, annotated_frame = detect_smoking(frame, camera)
                
                # 檢查是否偵測到吸菸
                if detection_data and detection_data["is_smoking"]:
                    cam_id = camera.id
                    now = datetime.now()

                    # 初始化該攝影機的計數器
                    if cam_id not in smoking_frame_counter:
                        smoking_frame_counter[cam_id] = 0
                    smoking_frame_counter[cam_id] += 1

                    # 若連續3幀偵測到吸菸才視為有效
                    if smoking_frame_counter[cam_id] >= DETECTION_STABLE_FRAMES:
                        # 冷卻時間檢查
                        last_time = last_detection_time.get(cam_id)
                        if not last_time or (now - last_time > DETECTION_COOLDOWN):
                            print(f"⚠️ [{camera.camera_name}] 偵測到穩定吸菸行為！")

                            if camera.enable_screenshot:
                                screenshot_path = save_screenshot(annotated_frame, camera, db)
                                detection_data["screenshot_path"] = screenshot_path

                            save_detection(detection_data, camera, db)
                            last_detection_time[cam_id] = now

                            await websocket.send_json({
                                "type": "alert",
                                "data": detection_data
                            })
                else:
                    # 若中斷吸菸，重設計數器
                    smoking_frame_counter[camera.id] = 0

                    
                    # 回傳警報
                    await websocket.send_json({
                        "type": "alert",
                        "data": detection_data
                    })
                
                # 回傳偵測結果(不含影像)
                await websocket.send_json({
                    "type": "detection_result",
                    "data": detection_data
                })
                
                # 更新最後上線時間
                camera.last_seen = datetime.now()
                db.commit()
    
    except WebSocketDisconnect:
        camera.is_online = False
        db.commit()
        print(f"📷 攝影機 [{camera.camera_name}] 已斷線")


# ==================== 偵測邏輯 ====================

def detect_smoking(frame, camera: Camera):

    """執行吸菸偵測"""
    if model is None:
        # 返回空的偵測結果
        return {
            "has_person": False,
            "has_cigarette": False,
            "is_smoking": False,
            "boxes": [],
            "max_confidence": 0
        }, frame
    
    # 執行推論
    results = model.predict(
        frame,
        conf=camera.confidence_threshold,
        iou=camera.iou_threshold,
        verbose=False
    )
    
    result = results[0]
    boxes = result.boxes

    # 檢查是否同時有人和香菸
    has_person = any(int(box.cls[0]) == 0 for box in boxes)
    has_cigarette = any(int(box.cls[0]) == 1 for box in boxes)
    
    detection_data = {
        "has_person": has_person,
        "has_cigarette": has_cigarette,
        "is_smoking": has_person and has_cigarette,
        "boxes": []
    }
    
    # 繪製偵測框
    annotated_frame = result.plot()
    
    # 收集框的資訊
    max_confidence = 0
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        
        if conf > max_confidence:
            max_confidence = conf
        
        detection_data["boxes"].append({
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "confidence": conf,
            "class": cls,
            "label": "cigarette" if cls == 0 else "person"
        })
    
    detection_data["max_confidence"] = max_confidence


    return detection_data, annotated_frame


def save_screenshot(frame, camera: Camera, db: Session):
    """儲存截圖"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"violation_{camera.id}_{timestamp}.jpg"
    filepath = SCREENSHOT_DIR / filename
    
    cv2.imwrite(str(filepath), frame)
    
    # return str(filepath)
    return filename


def save_detection(detection_data, camera: Camera, db: Session):
    """儲存偵測記錄到資料庫"""
    detection = Detection(
        user_id=camera.user_id,
        camera_id=camera.id,
        has_person=detection_data["has_person"],
        has_cigarette=detection_data["has_cigarette"],
        is_smoking=detection_data["is_smoking"],
        confidence=detection_data.get("max_confidence", 0),
        screenshot_path=detection_data.get("screenshot_path"),
        detection_details=json.dumps(detection_data["boxes"])
    )
    
    db.add(detection)
    db.commit()


# ==================== 其他 API ====================

@app.get("/")
async def root():
    return {
        "message": "吸菸監控系統 API v2.0",
        "version": "2.0",
        "features": ["多用戶支援", "多攝影機管理", "JWT 認證", "MySQL 資料庫"],
        "endpoints": {
            "auth": "/api/auth/*",
            "cameras": "/api/cameras",
            "detections": "/api/detections",
            "statistics": "/api/statistics",
            "websocket_upload": "/ws/upload/{api_key}"
        }
    }


@app.get("/api/screenshots/{filename}")
async def get_screenshot(filename: str):
    """取得截圖"""
    filepath = SCREENSHOT_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="截圖不存在")
    return FileResponse(filepath)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
