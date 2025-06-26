from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
from .base import BaseResp
import re

PHONE_NUMBER_REGEX = r"^1[3-9]\d{9}$"


class CustomerCreate(BaseModel):

    phone: str = Field(
        ...,
        max_length=20,
        pattern=PHONE_NUMBER_REGEX, # pattern 参数使用正则表达式字符串
        description="登录手机号 (11位数字)"
    )
    password: str = Field(..., min_length=8, description="密码 (最少8位)")
    name: str = Field(..., min_length=1, max_length=100, description="用户姓名或昵称")
    email: Optional[EmailStr] = Field(None, description="客户邮箱 (可选)")
    address: Optional[str] = Field(None, description="地址 (可选)")

    # 使用 @field_validator 和 re 模块进行服务端的严格校验
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        # 使用 re.match() 函数来执行正则表达式匹配
        if not re.match(PHONE_NUMBER_REGEX, v):
            raise ValueError('手机号码格式不正确')
        return v

class UpdateCustomer(BaseModel):
    # ... 其他字段 ...
    phone: Optional[str] = Field(None, max_length=20, pattern=PHONE_NUMBER_REGEX)
    # ... 其他字段 ...

    @field_validator('phone')
    @classmethod
    def validate_update_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(PHONE_NUMBER_REGEX, v):
            raise ValueError('手机号码格式不正确')
        return v


class CustomerItem(BaseModel):
    # 用于从数据库读取并返回给前端的模型
    id: int
    name: str
    email: Optional[str]
    phone: str
    address: Optional[str]
    registration_date: datetime

    class Config:
        from_attributes = True # 允许从 ORM 对象自动映射

class CustomerList(BaseResp):
    # 返回客户列表时使用
    data: List[CustomerItem] = Field([], description="客户列表")

class CustomerResponse(BaseResp):
    data: Optional[CustomerItem] = None


class CustomerSearch(BaseModel):
    """用于高级顾客搜索的输入模型"""
    name: Optional[str] = Field(None, description="顾客姓名 (模糊查询)")
    email: Optional[EmailStr] = Field(None, description="顾客邮箱 (模糊查询)")
    phone: Optional[str] = Field(None, description="顾客手机号 (模糊查询)")
