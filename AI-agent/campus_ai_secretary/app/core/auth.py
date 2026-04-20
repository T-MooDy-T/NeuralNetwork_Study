"""认证模块"""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from loguru import logger

from ..database.connection import SessionLocal
from ..database.models import User

# 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    """认证用户"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username, user_id=user_id, role=role)
        return token_data
        
    except JWTError as e:
        logger.warning(f"JWT 解析失败：{e}")
        raise credentials_exception


async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """获取当前活跃用户"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_user.username).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=400, detail="用户已禁用")
        return current_user
    finally:
        db.close()


async def get_current_admin_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


def init_admin_user():
    """初始化管理员账号"""
    db = SessionLocal()
    try:
        # 检查是否已有管理员
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            logger.info("管理员账号已存在")
            return
        
        # 创建默认管理员
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        admin = User(
            username=admin_username,
            password_hash=get_password_hash(admin_password),
            email="admin@campus.ai",
            nickname="管理员",
            role="admin",
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        logger.info(f"✅ 默认管理员账号已创建：{admin_username} / {admin_password}")
    except Exception as e:
        logger.error(f"创建管理员失败：{e}")
        db.rollback()
    finally:
        db.close()
