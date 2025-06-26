from fastapi import HTTPException, status
from tortoise.transactions import in_transaction
from core import Responses
from core.Responses import success
from crud import order as crud_order
from models.base import Order, OrderStatus, Customer, Product
from schemas import order as order_schemas


async def service_create_order_logic(order_data: order_schemas.CreateOrder):
    """
    创建新订单的完整业务逻辑，包含事务处理和库存检查。
    """
    async with in_transaction():
        # 1. 查询一次客户，并立即检查是否存在
        #    我们假设 crud_customer.get() 就是获取客户的函数
        customer = await Customer.get_or_none(id=order_data.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="指定的客户不存在")

        # 2. 创建主订单记录，总价初始化为 0
        #    直接使用上面获取到的 customer 对象
        new_order = await crud_order.create_order(customer=customer, total_amount=0)
        total_amount = 0

        # 3. 遍历所有订单项
        for item_data in order_data.items:
            product = await Product.get_or_none(id=item_data.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"ID为 {item_data.product_id} 的商品不存在")

            # 检查库存
            if product.stock_quantity < item_data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"商品 '{product.name}' 库存不足，剩余 {product.stock_quantity} 件。"
                )

            # 计算总价
            total_amount += product.price * item_data.quantity
            # 创建订单项
            await crud_order.create_order_item(new_order, product, item_data)

            # 扣减库存
            product.stock_quantity -= item_data.quantity
            await product.save()  # Tortoise ORM 也需要保存对product的修改

        # 4. 更新订单总价
        new_order.total_amount = total_amount
        await new_order.save()
        await new_order.fetch_related("customer", "items", "items__product")
        return Responses.success(data=new_order, msg="订单创建成功！")


async def service_get_order_by_id_logic(order_id: int):
    """获取单个订单，并预先加载关联数据"""
    order = await crud_order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"ID为 {order_id} 的订单不存在")

    # 【关键】使用 fetch_related 预先加载关联的对象，以便 Pydantic 序列化
    # 'items__product' 表示在加载 items 的同时，把 item 关联的 product 也加载出来
    await order.fetch_related("customer", "items", "items__product")
    return success(msg="订单获取成功！",data=order)


async def service_get_all_orders_logic(page: int, page_size: int):
    """获取订单列表，并预加载关联数据"""
    skip = (page - 1) * page_size
    orders_orm, total = await crud_order.get_multi(skip=skip, limit=page_size)

    # 对列表中的每个订单都预加载数据
    for order in orders_orm:
        await order.fetch_related("customer", "items", "items__product")
    return success(msg="获取订单列表成功！", data=orders_orm)


async def service_update_order_status_logic(order_id: int, order_data: order_schemas.UpdateOrder):
    """更新订单状态"""
    order = await crud_order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"ID为 {order_id} 的订单不存在")

    # 业务规则：已完成或已取消的订单不能再修改状态
    if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"无法更新状态为 '{order.status.value}' 的订单")

    order.status = order_data.status
    await order.save()
    await order.fetch_related("customer", "items", "items__product")
    return success(msg="订单更新成功！",data=order)   # 返回完整信息的订单


async def service_delete_order_logic(order_id: int):
    """删除订单的业务逻辑"""
    order = await crud_order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"ID为 {order_id} 的订单不存在")

    # 业务规则：只有待处理或已取消的订单可以被删除
    if order.status not in [OrderStatus.PENDING, OrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"无法删除状态为 '{order.status.value}' 的订单，请先取消。")

    # 注意：因为数据库表结构设置了 ON DELETE CASCADE，删除 Order 时，
    # 数据库会自动删除所有关联的 OrderItem 记录。
    # 如果要返还库存，需要在这里添加逻辑。
    await crud_order.remove(order)
    return success(msg="删除订单成功!")