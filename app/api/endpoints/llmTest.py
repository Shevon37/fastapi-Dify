import os

import mysql.connector
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from contextlib import asynccontextmanager
from typing import Union

# 导入我们定义好的 Schema 和全局配置
from schemas.sqlTester import (
    SQLTestRequest,
    TestSuccessResponse,
    TestErrorResponse,
    TestExecutionResult,
    TestErrorDetail
)
from config import settings

# --- 1. 准备工作 ---
llmTest_router = APIRouter(
    prefix="/api/test",
    tags=["SQL 通用安全测试引擎"],
)

try:
    db_credentials = settings.DB_CONFIG
except AttributeError:
    raise RuntimeError("配置文件(config.py)中缺少必要的数据库连接信息。")



@llmTest_router.post("/execute", summary="安全地测试任意单条SQL语句",
             response_model=Union[TestSuccessResponse, TestErrorResponse])
async def universal_sql_test_executor(request: SQLTestRequest):
    """
    本接口是智能SQL测试引擎的核心。
    - 在安全的事务沙箱中执行单条SQL并立即回滚。
    - 自动判断SQL操作类型。
    - 返回结构化的、包含智能诊断的成功或失败信息。
    """
    sql_command = request.sql.strip()

    if not sql_command:
        raise HTTPException(status_code=400, detail="SQL 语句不能为空。")

    # 自动判断操作类型
    sql_upper = sql_command.upper()
    operation_type = "UNKNOWN"
    if sql_upper.startswith("INSERT"):
        operation_type = "INSERT"
    elif sql_upper.startswith("UPDATE"):
        operation_type = "UPDATE"
    elif sql_upper.startswith("DELETE"):
        operation_type = "DELETE"
    elif sql_upper.startswith("SELECT"):
        operation_type = "SELECT"

    cnx = None
    try:
        # 在 try 块内部建立连接和事务
        cnx = mysql.connector.connect(**db_credentials)
        cursor = cnx.cursor(dictionary=True)
        cnx.start_transaction()

        cursor.execute(sql_command)

        # 根据操作类型，生成定制化的成功响应
        if operation_type == "SELECT":
            result_data = cursor.fetchall()
            return TestSuccessResponse(
                operation=operation_type,
                message="SQL 语法正确，查询可被执行。",
                result_preview=result_data[:5]  # 最多返回5条记录作为预览
            )
        else:  # 适用于 INSERT, UPDATE, DELETE
            rowcount = cursor.rowcount
            op_map = {"INSERT": "插入", "UPDATE": "更新", "DELETE": "删除"}
            success_message = f"测试操作成功：可以完成 {op_map.get(operation_type, '未知')} {rowcount} 条记录的操作（注：更改已回滚）。"

            return TestSuccessResponse(
                operation=operation_type,
                message=success_message,
                execution_result=TestExecutionResult(affected_rows=rowcount)
            )

    except mysql.connector.Error as err:
        # 如果发生任何数据库错误，进行智能诊断
        error_type, suggestion = "UNKNOWN_ERROR", "发生未知数据库错误，请检查SQL语法。"
        if err.errno == 1062:
            error_type, suggestion = "UNIQUE_CONSTRAINT_VIOLATION", f"违反了唯一性约束。试图插入或更新的值可能已在表中存在。"
        elif err.errno == 1452:
            error_type, suggestion = "FOREIGN_KEY_CONSTRAINT_FAILURE", f"外键约束失败。关联的其他表中不存在对应的记录。"
        elif err.errno == 1364:
            error_type, suggestion = "NOT_NULL_CONSTRAINT_VIOLATION", f"违反非空约束。有某个必需字段没有被提供值。"
        elif err.errno == 1451:
            error_type, suggestion = "FOREIGN_KEY_CONSTRAINT_FAILURE_ON_DELETE", f"违反外键约束，无法删除一个仍被其他表引用的记录。"
        elif err.errno == 1054:
            error_type, suggestion = "UNKNOWN_COLUMN", "列名不存在，请检查字段名是否拼写正确。"
        elif err.errno == 1146:
            error_type, suggestion = "TABLE_DOES_NOT_EXIST", "表名不存在，请检查 FROM 或 JOIN 子句中的表名是否正确。"

        error_detail = TestErrorDetail(type=error_type, suggestion=suggestion, raw_message=err.msg)
        return TestErrorResponse(operation=operation_type, error=error_detail)

    finally:
        # 无论如何都确保回滚和关闭
        if cnx and cnx.is_connected():
            print("--- 测试执行完毕，事务回滚 ---")
            cnx.rollback()
            cnx.close()
