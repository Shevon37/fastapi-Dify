import os
from dotenv import load_dotenv
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

# 加载环境变量（需要创建env文件）
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

DB_ORM_CONFIG = {
    "connections": {
        "default": {
            'engine': 'tortoise.backends.mysql',
            "credentials": {
                'host': os.getenv('BASE_HOST', '127.0.0.1'),
                'user': os.getenv('BASE_USER', 'root'),
                'password': os.getenv('BASE_PASSWORD', ''),
                'port': int(os.getenv('BASE_PORT', '3306')),
                'database': os.getenv('BASE_DB'),
                'charset': 'utf8mb4'
            }
        }
    },
    "apps": {
        "base": {
            "models": ["models.base"],
            "default_connection": "default"
        }
    },
    "use_tz": False,
    "timezone": 'Asia/Shanghai'
}


async def register_mysql(app: FastAPI):
    """
    使用 Tortoise-ORM 官方推荐的辅助函数来注册数据库。
    它会在 FastAPI 启动时自动完成初始化和建表，在关闭时自动关闭连接。
    """
    print("--- INFO: 正在配置 Tortoise ORM，将在应用启动时自动初始化... ---")
    register_tortoise(
        app,
        config=DB_ORM_CONFIG,
        generate_schemas=True,  # 告诉它在启动时建表
        add_exception_handlers=True,
    )
    print("--- INFO: Tortoise ORM 事件处理器已注册。 ---")