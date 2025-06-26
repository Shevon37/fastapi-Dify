from fastapi import APIRouter, status, Depends

from core.Security import get_current_customer
from schemas import order as order_schemas
from service import order as order_service
from core import Responses

# 此处为了方便进行调试，取消了校验的拦截。
# order_router = APIRouter(
#     prefix="/api/orders",
#     tags=["订单管理"],
#     dependencies=[Depends(get_current_customer)]
# )
order_router = APIRouter(
    prefix="/api/orders",
    tags=["订单管理"]
)

# 创建订单
@order_router.post("/create", response_model=order_schemas.SingleOrderResponse, status_code=status.HTTP_201_CREATED)
async def controller_create_order(order_data: order_schemas.CreateOrder):
    return await order_service.service_create_order_logic(order_data)

# 查询订单列表
@order_router.get("/get/list", response_model=order_schemas.OrderList)
async def controller_get_all_orders(page: int = 1, page_size: int = 10):
    return await order_service.service_get_all_orders_logic(page, page_size)

# 获取单个订单
@order_router.get("/get/{order_id}", response_model=order_schemas.SingleOrderResponse)
async def controller_get_order_by_id(order_id: int):
    return await order_service.service_get_order_by_id_logic(order_id)

# 更新订单
@order_router.post("/update/{order_id}", response_model=order_schemas.SingleOrderResponse)
async def controller_update_order_status(order_id: int, order_data: order_schemas.UpdateOrder):
    return await order_service.service_update_order_status_logic(order_id, order_data)

# 删除订单
@order_router.delete("/delete/{order_id}", status_code=status.HTTP_200_OK)
async def controller_delete_order(order_id: int):
    return await order_service.service_delete_order_logic(order_id)