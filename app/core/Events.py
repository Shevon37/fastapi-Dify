from typing import Callable
from fastapi import FastAPI
from database.mysql import register_mysql


def startup(app: FastAPI) -> Callable:
    """
    FastApi 启动完成事件
    :param app: FastApi
    :return: start_app
    """
    async def app_start() -> None: # 启动完成后触发
        print("FastAPI已启动")
        await register_mysql(app)

    return app_start

def stop(app: FastAPI) -> Callable:
    """
    FastApi 停止
    :param app: app:FastAPI
    :return: stop_app
    """
    async def stop_app() -> None:
        # APP停止时触发
        print("fastapi已停止")

    return stop_app