from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.Responses import success
from core.Security import create_access_token

from schemas import customer as customer_schemas
from service import customer as customer_service
from schemas import auth as auth_schemas


customer_router = APIRouter(
    prefix="/api/customers",
    tags=["客户管理"],
)


# 注册
@customer_router.post("/register", response_model=customer_schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
async def controller_register_customer_logic(customer_data: customer_schemas.CustomerCreate):
    """
    创建一个新客户。
    - `customer_data`: 请求体，FastAPI会用 CreateCustomer Schema来校验。
    - `response_model`: 指定了返回的数据会按照 CustomerInDB 的格式进行序列化。
    """
    return await customer_service.service_register_customer_logic(customer_data=customer_data)

# 登录
@customer_router.post("/login", response_model=auth_schemas.TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    顾客通过手机号和密码登录以获取 Access Token.

    在测试时，请使用 form-data 格式发送数据:
    - username: 你的手机号
    - password: 你的密码
    """
    # 调用 service 层进行认证
    customer = await customer_service.authenticate_customer(
        phone=form_data.username,  # FastAPI 的 OAuth2PasswordRequestForm 固定使用 username 字段
        password=form_data.password
    )

    # 如果 service 返回 None，说明认证失败，抛出 401 错误
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 认证成功，创建 JWT Token，使用客户的手机号作为唯一标识
    access_token = create_access_token(data={"sub": customer.phone})
    token_data = {"access_token": access_token, "token_type": "bearer"}

    # 4. 使用辅助函数封装成功响应
    return success(data=token_data, msg="登录成功")

# 读取客户列表
@customer_router.get("/get/list",response_model=customer_schemas.CustomerList)
async def get_all_customers(page: int = 1, page_size: int = 10):
    """
    获取客户列表。( 分页获取 )
    """
    return await customer_service.service_get_all_customers(page,page_size)

# 获取单个客户信息
@customer_router.get("/get/{customer_id}", response_model=customer_schemas.CustomerResponse)
async def get_customer_by_id(customer_id: int):
    return await customer_service.service_get_customer_by_id(customer_id)

# 更新客户信息
@customer_router.post("/update/{customer_id}", response_model=customer_schemas.CustomerResponse)
async def update_customer(customer_id: int, customer_data: customer_schemas.UpdateCustomer):
    """
    更新指定ID的客户信息。
    """
    return await customer_service.service_update_customer(customer_id, customer_data)


# 删除
@customer_router.delete("/delete/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int):
    """
    删除指定ID的客户。
    """
    return await customer_service.service_delete_customer(customer_id)

