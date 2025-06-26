from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from schemas.base import BaseResp

class CreateProduct(BaseModel):
    name: str = Field(..., max_length=255, description="商品名称")
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="价格")
    stock_quantity: int = Field(0, ge=0, description="库存数量")


class UpdateProduct(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)

class ProductItem(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductList(BaseResp):
    data: List[ProductItem] = Field([], description="商品列表")

class ProductResponse(BaseResp):
    data: Optional[ProductItem] = None
