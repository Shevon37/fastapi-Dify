from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import DoesNotExist
from models.base import Product
from schemas import product as product_schemas

from core.Responses import success, fail


async def service_create_product(product_data: product_schemas.CreateProduct):
    new_product = await Product.create(**product_data.model_dump())
    return success(msg="成功创建商品！",data=new_product)


async def service_get_all_products(page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    products = await Product.all().offset(skip).limit(page_size)
    return success(msg="获取商品列表成功！", data=products)


async def service_get_product_by_id(product_id: int):
    try:
        product = await Product.get(id=product_id)
        return success(msg="获取商品列表成功！", data=product)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID为 {product_id} 的商品不存在")


async def service_update_product(product_id: int, product_data: product_schemas.UpdateProduct):
    try:
        product_obj = await Product.get(id=product_id)
        if not product_obj:
            fail(msg="没有该商品！")
        update_data = product_data.model_dump(exclude_unset=True)
        if not update_data:
            # 如果更新数据为空，直接告诉客户端这是个无效请求
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请求体中没有提供任何需要更新的数据。"
            )
        await product_obj.update_from_dict(update_data)
        await product_obj.save()
        new_product = await Product.get(id=product_id)
        return success(msg="更新商品成功！", data=new_product)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID为 {product_id} 的商品不存在")


async def service_delete_product(product_id: int):
    try:
        product_obj = await Product.get(id=product_id)
        await product_obj.delete()
        return success(msg="成功删除")
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID为 {product_id} 的商品不存在")