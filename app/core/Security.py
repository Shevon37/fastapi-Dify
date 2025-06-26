from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from config import settings
from models.base import Customer
from schemas.auth import TokenData

# CryptContext 的初始化保持不变，这是正确的
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码和哈希密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码的哈希值"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT Access Token

    :param data: 需要编码到 token 中的数据 (payload)
    :param expires_delta: 可选的过期时间增量
    :return: 编码后的 JWT token 字符串
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # 默认使用从 settings 中读取的过期分钟数
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # 使用从 settings 中读取的密钥和算法
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


# 校验需要依赖的函数
# 若在接口参数中加了Depends(get_current_customer)，则通过这个接口校验token是否有效，并返回用户
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
async def get_current_customer(token: str = Depends(oauth2_scheme)) -> Customer:
    """
    一个依赖项函数，它会完成以下所有工作：
    1. 从请求头中提取 Token。
    2. 验证 Token 的签名和过期时间。
    3. 解码 Token，获取里面的用户信息（手机号）。
    4. 根据手机号从数据库中查询用户。
    5. 返回用户 ORM 对象。
    如果任何一步失败，它会直接抛出 HTTP 异常。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        phone: str = payload.get("sub")
        if phone is None:
            raise credentials_exception

        token_data = TokenData(sub=phone)

    except (JWTError, ValidationError):
        raise credentials_exception

    # 根据从 token 中获取的手机号，去数据库查询用户
    customer = await Customer.get_or_none(phone=token_data.sub)
    if customer is None:
        raise credentials_exception

    return customer