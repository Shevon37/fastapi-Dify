from pydantic import BaseModel, Field
from typing import Optional, Union, Any, Literal

# 【修改】输入模型现在只接收一个 SQL 字符串，不再需要 table_name。
class SQLTestRequest(BaseModel):
    sql: str = Field(..., description="由AI生成的、待测试的单条SQL语句")

# --- 输出模型 (用于结构化返回) ---

class TestExecutionResult(BaseModel):
    affected_rows: int

class TestErrorDetail(BaseModel):
    type: str = Field(..., description="程序定义的错误类型")
    suggestion: str = Field(..., description="给AI或用户的修正建议")
    raw_message: str = Field(..., description="从数据库返回的原始错误信息")

class TestSuccessResponse(BaseModel):
    status: Literal["valid"] = "valid"
    operation: str
    message: str
    result_preview: Optional[Any] = Field(None, description="查询结果预览（最多5条）")
    execution_result: Optional[TestExecutionResult] = None

class TestErrorResponse(BaseModel):
    status: Literal["invalid"] = "invalid"
    operation: str
    error: TestErrorDetail
