from typing import List, Tuple, Optional
from tortoise.transactions import in_transaction

from models.base import Order, OrderItem, Product, Customer
from schemas.order import CreateOrderItem

# --- Create ---
async def create_order(customer: Customer, total_amount: float = 0.0) -> Order:
    """仅创建订单主体"""
    return await Order.create(customer=customer, total_amount=total_amount)

async def create_order_item(order: Order, product: Product, item_data: CreateOrderItem) -> OrderItem:
    """创建订单项"""
    return await OrderItem.create(
        order=order,
        product=product,
        quantity=item_data.quantity,
        price_per_unit=product.price
    )

# --- Read ---
async def get(order_id: int) -> Optional[Order]:
    """根据ID获取单个订单"""
    return await Order.get_or_none(id=order_id)

async def get_multi(skip: int = 0, limit: int = 10) -> Tuple[List[Order], int]:
    """获取订单列表（带分页）"""
    orders = await Order.all().offset(skip).limit(limit).order_by('-order_date')
    total = await Order.all().count()
    return orders, total

# --- Update ---
async def update(order: Order) -> Order:
    """保存订单对象的更改"""
    await order.save()
    return order

# --- Delete ---
async def remove(order: Order) -> None:
    """删除订单"""
    await order.delete()