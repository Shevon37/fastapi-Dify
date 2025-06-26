from fastapi import APIRouter, HTTPException, status
from schemas import product as product_schemas
from service.product import service_create_product, service_get_all_products, service_get_product_by_id, \
    service_update_product, service_delete_product

product_router = APIRouter(
    prefix="/api/products",
    tags=["商品管理"],
)

# 创建商品
@product_router.post("/create", response_model=product_schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
async def controller_create_product(product_data: product_schemas.CreateProduct):
    print(product_data)
    return await service_create_product(product_data)

# 读取商品列表
@product_router.get("/get/list", response_model=product_schemas.ProductList)
async def controller_get_all_products(page: int = 1, page_size: int = 10):
    return await service_get_all_products(page, page_size)

# 读取单个商品
@product_router.get("/get/{product_id}", response_model=product_schemas.ProductResponse)
async def controller_get_product_by_id(product_id: int):
    return await service_get_product_by_id(product_id)

# 更新商品
@product_router.post("/update/{product_id}", response_model=product_schemas.ProductResponse)
async def controller_update_product(product_id: int, product_data: product_schemas.UpdateProduct):
    return await service_update_product(product_id, product_data)

# 删除商品
@product_router.delete("delect/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def controller_delete_product(product_id: int):
    return await service_delete_product(product_id)