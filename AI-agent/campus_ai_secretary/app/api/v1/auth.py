"""认证 API"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
from loguru import logger

from ...database.connection import get_db
from ...database.models import User
from ...core.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    Token,
    TokenData,
    get_current_user,
    get_current_admin_user,
    init_admin_user
)

router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    request: Request,
    username: str = Form(None),
    password: str = Form(None),
    db: Session = Depends(get_db)
):
    """用户登录获取令牌"""
    if not username or not password:
        try:
            body = await request.json()
            username = body.get('username')
            password = body.get('password')
        except Exception as e:
            logger.warning(f"无法解析请求体: {e}")
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="用户名和密码不能为空"
        )
    
    user = authenticate_user(db, username, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    # 更新最后登录时间
    from datetime import datetime
    user.last_login = datetime.now()
    db.commit()
    
    # 创建令牌
    access_token_expires = timedelta(minutes=1440)  # 24 小时
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    logger.info(f"用户登录：{user.username}")
    
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1440,
        "user": {
            "username": user.username,
            "user_id": user.id,
            "role": user.role
        }
    }


@router.get("/me", summary="获取当前用户信息")
async def get_me(current_user: TokenData = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {
        "username": current_user.username,
        "user_id": current_user.user_id,
        "role": current_user.role
    }


@router.post("/register", summary="用户注册")
async def register(
    username: str,
    password: str,
    email: str = None,
    db: Session = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user = User(
        username=username,
        password_hash=get_password_hash(password),
        email=email,
        role="user"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"新用户注册：{username}")
    
    return {"message": "注册成功", "user_id": user.id}
