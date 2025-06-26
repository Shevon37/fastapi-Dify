# AI Agent 智能 SQL 测试与业务引擎
## 1. 项目简介
本项目是一个基于 FastAPI 和 Dify 构建的后端服务，旨在探索大型语言模型（LLM）在软件工程领域的深度应用。项目核心包含两大功能模块：

### 智能业务操作模块: 
实现了一套完整的、基于真实电商场景的后端业务 API。通过与 Dify 工作流结合，可以实现用自然语言驱动后端服务，完成顾客注册、下单等真实的增删改查操作。这充分展示了如何通过 ORM 调用来构建安全、可靠的 AI Agent 后端。

### 智能 SQL 测试引擎: 
提供了一系列专用的、安全的数据库测试接口。AI Agent 可以被赋予“QA工程师”的角色，自动设计并生成针对唯一性约束、外键关联、数据类型、边界值等边缘情况的 SQL 测试用例，并通过事务回滚机制在沙箱环境中安全执行，最终输出详细的自动化测试与诊断报告。

这个项目完整地体现了从基础业务实现到高级智能测试的演进过程，是学习和实践 AI Agent 与后端服务结合的最佳范例。

## 2. 技术栈
后端框架: FastAPI

数据库 ORM: Tortoise-ORM

数据库驱动: mysql-connector-python (用于原生SQL测试), aiomysql (用于ORM)

数据校验: Pydantic

认证授权: JWT + OAuth2 (Passlib, python-jose)

环境配置: python-dotenv

AI Agent 平台: Dify

## 3. 项目结构

/fastapi_study
├── api/
│   └── endpoints/         # 存放所有路由（Controller）文件，如 customer.py, order.py, llmTest.py
├── core/
│   ├── config.py          # Pydantic 配置管理
│   ├── dependencies.py    # 认证依赖项 (门禁)
│   ├── Responses.py       # 统一的响应封装函数
│   └── Security.py        # 密码哈希、JWT Token 生成等安全工具
├── crud/
│   └── *.py               # 数据访问层 (DAL)，封装最原始的数据库读写
├── database/
│   └── mysql.py           # Tortoise-ORM 数据库配置与初始化
├── models/
│   └── base.py            # Tortoise-ORM 数据模型定义
├── schemas/
│   └── *.py               # Pydantic 数据结构定义（API的输入输出规范）
├── service/
│   └── *.py               # 业务逻辑层 (Service)，处理核心业务规则
├── .env                   # 环境变量配置文件（需自行创建）
├── main.py                # FastAPI 应用主入口
├──requirements.txt        # 项目依赖
├──config.py               # Pydantic 配置管理
├──README.md               # 阅读文档
├──test_example.md         # SQL测试工作流输出示例        
└── table.sql              # 数据库原始SQL文件

## 4. 数据库设计
系统围绕一个标准的电商业务场景设计，核心是顾客（Customers）、商品（Products）和他们之间产生的订单（Orders）。

(你原来写的这部分数据库表结构解释非常详细和专业，我将它原封不动地保留，并稍微调整了标题层级以优化阅读体验)

### 4.1. customers (顾客/用户表)
职责: 存储所有注册用户的核心信息，既是业务上的“顾客”，也是系统中可以登录的“用户”。

关键字段: id, phone (登录凭证, NOT NULL, UNIQUE), hashed_password (NOT NULL), email (UNIQUE), name, address。

### 4.2. products (商品表)
职责: 存储所有可供销售的商品信息。

关键字段: id, name, price (DECIMAL), stock_quantity。

### 4.3. orders (订单主表)
职责: 存储每笔订单的总体信息，是连接顾客和购买行为的桥梁。

核心关联: 与 customers 表为多对一关系。

删除影响 (ON DELETE RESTRICT): 为保证数据完整性，禁止删除尚有关联订单的顾客。

### 4.4. order_items (订单详情表)
职责: 连接 orders 和 products 的中间表，记录订单中的具体商品项。

核心关联: 同时与 orders 和 products 表关联。

删除影响:

级联删除 (ON DELETE CASCADE for order_id): 删除订单时，会自动删除其下的所有订单项。

限制删除 (ON DELETE RESTRICT for product_id): 为保证历史订单数据完整，禁止删除已被下单的商品。

## 5. 快速开始
## 5.1. 环境准备
确保你的电脑已安装 Python 3.8+ 和 MySQL 数据库。

本项目推荐使用虚拟环境进行管理。

## 5.2. 安装与配置

### 1.创建并激活虚拟环境 (以 conda 为例)

```
conda create -n fastapi_env python=3.11
conda activate fastapi_env
```
若不使用 conda
```
# 若无, 使用venv
python -m venv venv

# 激活虚拟环境
# 使用macos/linux：
source ./venv/bin/activate
# windows：
.\venv\Scripts\activate
```

### 2.安装依赖
```
pip install -r requirements.txt
```


### 3.创建数据库

请在你的 MySQL 中手动创建一个数据库，例如 dify_fastapi_project。

### 4.配置环境变量

在项目根目录下，复制 .env.example (如果提供) 或手动创建一个名为 .env 的文件。

修改 .env 文件中的数据库连接信息（BASE_HOST, BASE_USER, BASE_PASSWORD, BASE_DB 等），使其与你的本地数据库配置一致。

## 5.3. 运行项目
启动服务
```
# 在项目根目录（包含 app 文件夹的那一级）运行
uvicorn app.main:app --reload
```
--reload 参数会在你修改代码后自动重启服务，非常适合开发阶段。

## 访问 API 文档

服务启动后，在浏览器中打开 http://127.0.0.1:8000/docs。
你将看到 FastAPI 自动生成的交互式 API 文档 (Swagger UI)，可以在这里直接对所有接口进行测试。




