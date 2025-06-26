from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from .base import BaseResp
from .product import ProductItem  # 导入 ProductItem 用于嵌套显示
from .customer import CustomerItem  # 导入 CustomerItem 用于嵌套显示

# 从 tortoise 模型文件导入 OrderStatus 枚举
from models.base import OrderStatus


# 创建订单时，每个订单项需要的信息
class CreateOrderItem(BaseModel):
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(..., gt=0, description="数量")


# 从数据库返回给前端的订单项信息
class OrderItem(BaseModel):
    id: int
    quantity: int
    price_per_unit: Decimal
    product: ProductItem  # 嵌套显示完整的商品信息

    class Config:
        from_attributes = True


# 创建订单时需要的信息
class CreateOrder(BaseModel):
    customer_id: int = Field(..., description="客户ID")
    items: List[CreateOrderItem] = Field(..., min_length=1, description="订单商品列表")


# 更新订单时允许修改的信息
class UpdateOrder(BaseModel):
    status: Optional[OrderStatus] = None


class OrderItemSchema(BaseModel):
    id: int
    quantity: int
    price_per_unit: Decimal

    # 【嵌套】在这里，我们不只显示 product_id，而是显示完整的商品信息
    product: ProductItem

    class Config:
        from_attributes = True  # V1 写法 (或 V2 的 from_attributes = True)


# --- 订单 Schema (对应 orders 表的一行) ---
class OrderSchema(BaseModel):
    id: int
    order_date: datetime
    status: OrderStatus
    total_amount: Optional[Decimal]

    # 【嵌套】显示完整的客户信息
    customer: CustomerItem

    # 【嵌套列表】显示这张订单包含的所有“订单项”
    items: List[OrderItemSchema] = []

    class Config:
        orm_mode = True  # V1 写法

# 返回订单列表时使用
class OrderList(BaseResp):
    data: List[OrderSchema] = Field([], description="订单列表")

# 【新增】为“获取单个订单”接口专门创建一个响应模型
class SingleOrderResponse(BaseResp):
    # 用具体的 OrderSchema 类型来覆盖父类中宽泛的 data 字段
    # Optional 表示在某些情况下（比如查询失败的业务场景）data可以为null
    data: Optional[OrderSchema] = None