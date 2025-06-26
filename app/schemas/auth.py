from pydantic import BaseModel
from typing import Optional

# 导入我们通用的响应基类
from .base import BaseResp

class Token(BaseModel):
    """
    定义了登录成功后返回的 token 结构
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    定义了 JWT Token 中 payload (载荷) 的数据结构
    'sub' (subject) 是一个标准字段，我们用它来存放用户的唯一标识（手机号）
    """
    sub: Optional[str] = None


class TokenResponse(BaseResp):
    """
    定义了 /auth/login 接口最终返回的完整响应体结构
    """
    # data 字段的内容应该是一个 Token 对象
    data: Optional[Token] = None