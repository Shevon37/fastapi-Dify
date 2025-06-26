from tortoise.models import Model
from tortoise import fields
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Customer(Model):
    # 这是数据库中的列，用 tortoise.fields 定义
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    phone = fields.CharField(max_length=20, unique=True)
    email = fields.CharField(max_length=100, unique=True, null=True)
    hashed_password = fields.CharField(max_length=128)
    address = fields.TextField(null=True)
    registration_date = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "customers"
        app = "base"

class Product(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "products"
        app = "base"

class Order(Model):
    id = fields.IntField(pk=True)
    customer = fields.ForeignKeyField(
        "base.Customer",
        related_name="orders",
        on_delete=fields.RESTRICT
    )
    order_date = fields.DatetimeField(auto_now_add=True)
    status = fields.CharEnumField(OrderStatus, default=OrderStatus.PENDING)
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        table = "orders"
        app = "base"

class OrderItem(Model):
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField(
        "base.Order",
        related_name="items",
        on_delete=fields.CASCADE
    )
    product = fields.ForeignKeyField(
        "base.Product",
        related_name="order_items",
        on_delete=fields.RESTRICT
    )
    quantity = fields.IntField()
    price_per_unit = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "order_items"
        app = "base"