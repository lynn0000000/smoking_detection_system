from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from server.database import get_db, User
from server.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import secrets

# 密碼加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer Token
security = HTTPBearer()


# ==================== 密碼處理 ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """將密碼加密"""
    # 限制密碼長度避免 bcrypt 72 bytes 限制
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

# ==================== JWT Token ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """建立 JWT Access Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解析 JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ==================== 用戶認證 ====================

def authenticate_user(db: Session, username: str, password: str):
    """驗證用戶登入"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """取得當前登入用戶 (用於 API 路由保護)"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用戶已被停用")
    
    return user


def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """檢查是否為管理員"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="權限不足")
    return current_user


# ==================== 攝影機 API Key ====================

def generate_camera_api_key() -> str:
    """產生攝影機 API Key"""
    return secrets.token_urlsafe(32)


def verify_camera_api_key(api_key: str, db: Session):
    """驗證攝影機 API Key"""
    from server.database import Camera
    camera = db.query(Camera).filter(Camera.api_key == api_key).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的攝影機 API Key"
        )
    return camera


# ==================== Pydantic 模型 (用於 API) ====================

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """用戶註冊"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """用戶登入"""
    username: str
    password: str


class Token(BaseModel):
    """Token 回應"""
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    """用戶資訊回應"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
