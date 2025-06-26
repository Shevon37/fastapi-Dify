# app/schemas/sql.py
from pydantic import BaseModel

# 定义API请求体的数据结构
class SQLQuery(BaseModel):
    sql: str