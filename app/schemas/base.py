from typing import List
from pydantic import BaseModel, Field


class BaseResp(BaseModel):
    code: int = Field(description="状态码")
    message: str = Field(description="信息")
    data: List = Field(description="数据")
