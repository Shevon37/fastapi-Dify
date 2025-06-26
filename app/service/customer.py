from fastapi import APIRouter, HTTPException, status
from typing import List

# 导入 Tortoise ORM 的模型和异常
from tortoise.exceptions import DoesNotExist, IntegrityError

from core.Security import get_password_hash, verify_password
from models.base import Customer
# 导入我们之前创建的 Pydantic Schemas
from schemas import customer as customer_schemas
from schemas.base import BaseResp
from core.Responses import success

from core import Responses
from schemas.customer import CustomerSearch


async def service_register_customer_logic(customer_data: customer_schemas.CustomerCreate):
    """
    【最终修正版】在 Service 层统一处理所有注册逻辑
    - 检查手机号和邮箱是否存在
    - 对密码进行哈希处理
    - 创建新用户
    - 返回封装好的成功响应
    """
    # 业务逻辑 1: 检查手机号是否已存在
    if await Customer.get_or_none(phone=customer_data.phone):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"注册失败：手机号 '{customer_data.phone}' 已被注册。"
        )

    # 业务逻辑 2: 检查邮箱是否存在 (如果用户提供了邮箱)
    if customer_data.email and await Customer.get_or_none(email=customer_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"注册失败：邮箱 '{customer_data.email}' 已被使用。"
        )

    # 【核心修正】准备要存入数据库的数据
    # 1. 将 Pydantic 输入模型转换为字典，但使用 exclude 参数排除掉'password'字段，
    #    因为它不能被直接存储。
    #    Pydantic V1 使用 .dict()，V2 使用 .model_dump()
    customer_dict_to_create = customer_data.dict(exclude={'password'})

    # 2. 从输入数据中获取明文密码，并调用安全工具进行哈希
    hashed_password_to_store = get_password_hash(customer_data.password)

    # 3. 直接在这里调用 ORM 进行创建，传入普通数据和【哈希后的密码】
    #    这里的 hashed_password=... 对应的是 Customer ORM 模型里的字段名
    new_customer = await Customer.create(
        **customer_dict_to_create,
        hashed_password=hashed_password_to_store
    )

    # 【修正】不再需要多余的查询，Customer.create 已经返回了完整的对象
    # created_customer = await Customer.get(id=new_customer.id)

    # 直接使用创建成功后返回的 new_customer 对象，并封装成成功响应
    # FastAPI 会在后台自动处理 ORM 对象的序列化
    return success(msg="注册成功！", data=new_customer)


async def authenticate_customer(phone: str, password: str):
    """
    【新增】认证客户（登录）的业务逻辑
    1. 根据手机号从数据库查找用户。
    2. 如果找到用户，验证其密码。
    3. 验证成功则返回用户对象，否则返回 None。
    """
    # 1. 直接在 service 层查询数据库
    customer = await Customer.get_or_none(phone=phone)

    # 2. 验证用户是否存在以及密码是否正确
    if not customer or not verify_password(password, customer.hashed_password):
        return None

    # 3. 认证成功，返回完整的 Customer ORM 对象
    return customer

async def service_create_customer(customer_data: customer_schemas.CustomerCreate):
    """
    【健壮版】创建一个新客户，并处理可能发生的错误。
    """
    try:
        # 我们把数据库操作放在 try 块中

        new_customer_orm = await Customer.create(**customer_data.model_dump())

        # 只有成功时，代码才会执行到这里
        # 将 ORM 对象转换为 Pydantic Schema，以便进行序列化
        created_customer = await Customer.get_or_none(id=new_customer_orm.id)
        # 使用你的辅助函数返回成功响应
        return Responses.success(msg="成功创建新用户！", data=created_customer)

    except IntegrityError:
        # 如果捕获到 IntegrityError，通常意味着违反了数据库的唯一性约束
        # （在我们的例子里，最可能就是 email 重复了）
        # 我们应该返回一个表示“冲突”的 HTTP 409 错误
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"创建失败：电话 '{customer_data.phone}' 可能已经存在。"
        )

    except Exception as e:
        # 捕获所有其他可能的意外错误，返回通用的服务器错误
        # 这是一个兜底，保证程序不会因为未知错误而崩溃
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发生未知错误：{e}"
        )

async def service_get_all_customers(page: int = 1, page_size: int = 10):
    """
    获取客户列表。
    """
    customers = await Customer.all().offset(page).limit(page_size)
    return success(msg="成功查询",data=customers)



async def service_get_customer_by_id(customer_id: int):
    try:
        # get_or_none 会在找不到时返回 None，比 get() 然后 try/except 更简洁
        customer = await Customer.get_or_none(id=customer_id)
        if not customer:
            # 仍然使用 HTTPException 来返回非 200 的标准 HTTP 错误
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID为 {customer_id} 的客户不存在")
        return success(msg="查找成功！",data=customer) # FastAPI 会自动序列化
    except Exception as e:
        # 其他数据库错误等
        raise HTTPException(status_code=500, detail=str(e))


# --- 3. 更新 (Update) ---
async def service_update_customer(customer_id: int, customer_data: customer_schemas.UpdateCustomer):
    """
    更新指定ID的客户信息。
    """
    try:
        customer_obj = await Customer.get_or_none(id=customer_id)
        # model_dump(exclude_unset=True) 只获取用户明确传入的字段进行更新
        update_data = customer_data.model_dump(exclude_unset=True)
        if not customer_obj or not update_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID为 {customer_id} 的客户不存在")


        # 使用 update_from_dict 方法更新字段
        await customer_obj.update_from_dict(update_data)
        await customer_obj.save()  # 调用 save() 方法将更改保存到数据库
        return Responses.success(msg="更新成功！", data=customer_obj)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID为 {customer_id} 的客户不存在")


async def service_delete_customer(customer_id: int):
    """
    删除指定ID的客户。
    """
    try:
        customer_obj = await Customer.get(id=customer_id)
        await customer_obj.delete()  # 调用 delete() 方法删除记录
        # 删除成功通常返回 204 No Content，不需要响应体
        return success(msg="成功删除用户！")
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID为 {customer_id} 的客户不存在")


# 模糊查询：便于llm进行查找
async def search_customers_logic(search_params: CustomerSearch) -> List[Customer]:
    """根据一个或多个条件动态搜索顾客"""
    query = Customer.all()

    if search_params.name:
        query = query.filter(name__icontains=search_params.name)

    if search_params.email:
        query = query.filter(email__icontains=search_params.email)

    if search_params.phone:
        query = query.filter(phone__icontains=search_params.phone)

    return await query.order_by('-registration_date')