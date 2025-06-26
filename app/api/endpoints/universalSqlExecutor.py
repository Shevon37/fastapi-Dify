import mysql.connector
from fastapi import APIRouter
from typing import List

from schemas.universalSql import SQLExecutionRequest, SingleStatementResult, SQLExecutionResponse
from config import settings

universalSqlExecutor_router = APIRouter(
    prefix="/api/universalSql",
    tags=["通用SQL执行引擎"],
)

# 从 settings 安全地构建数据库连接证书
try:
    db_credentials = settings.DB_CONFIG
except AttributeError:
    raise RuntimeError("配置文件(config.py)中缺少必要的数据库连接信息。")


@universalSqlExecutor_router.post("/execute-batch", response_model=SQLExecutionResponse, summary="安全地执行一批SQL语句")
async def execute_sql_batch(request: SQLExecutionRequest):
    """
    接收一个SQL语句列表，并在单个事务中原子性地执行它们。
    - 如果所有SQL都成功执行，则【提交】整个事务，使更改生效。
    - 如果批处理中有【任何一条】SQL失败，则【回滚】整个事务，所有之前的操作都会被撤销。
    """
    batch_results: List[SingleStatementResult] = []
    cnx = None
    # 【核心修改】增加一个错误标记
    batch_has_error = False

    try:
        cnx = mysql.connector.connect(**db_credentials)
        cursor = cnx.cursor(dictionary=True)
        # 开启一个总的事务
        cnx.start_transaction()

        # 遍历用户传入的每一条SQL语句
        for sql_command in request.sql_batch:
            sql_command = sql_command.strip()
            if not sql_command:
                continue

            try:
                # 只有在之前的步骤都没有出错时，才尝试执行新的SQL
                if not batch_has_error:
                    cursor.execute(sql_command)

                    if sql_command.upper().startswith('SELECT'):
                        result_data = cursor.fetchall()
                    else:
                        result_data = {"affected_rows": cursor.rowcount}

                    batch_results.append(SingleStatementResult(
                        original_sql=sql_command,
                        status="success",
                        result_data=result_data
                    ))
                else:
                    # 如果批处理中已经出错了，后续的SQL直接标记为跳过（也可以标记为失败）
                    batch_results.append(SingleStatementResult(
                        original_sql=sql_command,
                        status="error",
                        error_message="Skipped due to previous error in batch."
                    ))

            except mysql.connector.Error as err:
                # 【核心修改】一旦有错误发生，就设置错误标记
                batch_has_error = True
                batch_results.append(SingleStatementResult(
                    original_sql=sql_command,
                    status="error",
                    error_message=err.msg
                ))

    except mysql.connector.Error as err:
        batch_has_error = True
        batch_results.append(SingleStatementResult(
            original_sql="Database Connection",
            status="error",
            error_message=f"无法连接到数据库: {err.msg}"
        ))

    finally:
        # 【核心修改】根据错误标记，决定是提交还是回滚
        if cnx and cnx.is_connected():
            if batch_has_error:
                print("--- 批处理中发生错误，事务回滚 ---")
                cnx.rollback()
                final_status = "rolled_back"
            else:
                print("--- 批处理全部成功，事务提交 ---")
                cnx.commit()
                final_status = "committed"
            cnx.close()
        else:
            final_status = "rolled_back"  # 连接失败也算回滚

    return SQLExecutionResponse(batch_results=batch_results, final_status=final_status)