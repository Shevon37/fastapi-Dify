from fastapi import APIRouter

from api.endpoints.llmTest import llmTest_router
from api.endpoints.customer import customer_router
from api.endpoints.order import order_router
from api.endpoints.product import product_router
from api.endpoints.universalSqlExecutor import universalSqlExecutor_router

router = APIRouter()
router.include_router(customer_router)
router.include_router(product_router)
router.include_router(order_router)
router.include_router(llmTest_router) # 用于SQL测试语句的接口（不提交事务）
router.include_router(universalSqlExecutor_router) # 用于执行通用SQL语句的接口（会真正修改数据库）