from pydantic import BaseModel, Field
from typing import List, Optional, Any, Literal

class SQLExecutionRequest(BaseModel):
    """接收一个或多个待执行的SQL语句列表"""
    sql_batch: List[str] = Field(..., description="包含多条SQL语句的列表")

class SingleStatementResult(BaseModel):
    """单个SQL语句的执行结果"""
    original_sql: str = Field(..., description="原始的SQL语句")
    status: Literal["success", "error"] = Field(..., description="执行状态")
    result_data: Optional[Any] = Field(None, description="成功时的返回数据（查询结果或影响行数）")
    error_message: Optional[str] = Field(None, description="失败时的错误信息")

class SQLExecutionResponse(BaseModel):
    """最终返回的、包含所有语句结果的列表"""
    batch_results: List[SingleStatementResult]
    final_status: Literal["committed", "rolled_back"] = Field(..., description="整个事务的最终状态")