import os

from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    # 调试模式
    DEBUG: bool = True
    # 项目信息
    VERSION: str = "0.0.1"
    PROJECT_NAME: str = "app"
    DESCRIPTION: str = '<a href="/redoc" target="_blank">redoc</a>'

    # 数据库配置
    DB_CONFIG = {
        'host': os.getenv('BASE_HOST', '127.0.0.1'),
        'user': os.getenv('BASE_USER', 'root'),
        'password': os.getenv('BASE_PASSWORD', '1234'),
        'port': int(os.getenv('BASE_PORT', '3306')),
        'database': os.getenv('BASE_DB', 'dify_test'),
        'charset': 'utf8mb4'
    }

    JWT_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60


settings = Config()