--- 原始SQL语句 ---

-- 删除已存在的表（如果需要重置）

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- ----------------------------

-- 客户表 (customers)

-- ----------------------------

CREATE TABLE `customers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(100) UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20) NOT NULL UNIQUE,
    `hashed_password` VARCHAR(128) NOT NULL,
    `address` TEXT,
    `registration_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT='存储顾客（系统用户）的信息';


-- ----------------------------

-- 商品表 (products)

-- ----------------------------

CREATE TABLE `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `price` DECIMAL(10, 2) NOT NULL,
    `stock_quantity` INT NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT='存储商品信息，包括价格和库存';


-- ----------------------------

-- 订单表 (orders)

-- ----------------------------

CREATE TABLE `orders` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_id` INT NOT NULL,
    `order_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `status` ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') NOT NULL DEFAULT 'pending',
    `total_amount` DECIMAL(10, 2),
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`) ON DELETE RESTRICT
) COMMENT='存储订单的总体信息和状态';


-- ----------------------------

-- 订单详情表 (order_items)

-- ----------------------------

CREATE TABLE `order_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL,
    `price_per_unit` DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON DELETE RESTRICT
) COMMENT='连接订单和商品，记录每个订单包含的具体商品和数量';



-- ----------------------------
-- 插入初始模拟数据
-- ----------------------------

-- 【核心修改】插入客户数据时，增加了 hashed_password 字段
-- 注意：这里使用了一个示例哈希值，你应该替换成你自己生成的
SET @hashed_password = '$2b$12$EixZaYVK1x7v2R4pDMxM9.e.2Y.P.5c.Y6k.J.G.5c.Y6k.J.G.5';

INSERT INTO `customers` (`name`, `email`, `phone`, `address`, `hashed_password`) VALUES
('张三', 'zhangsan@example.com', '13800138000', '北京市朝阳区', @hashed_password),
('李四', 'lisi@example.com', '13900139000', '上海市浦东新区', @hashed_password),
('王五', 'wangwu@example.com', '13700137000', '深圳市南山区', @hashed_password);

-- 插入商品
INSERT INTO `products` (`name`, `description`, `price`, `stock_quantity`) VALUES
('笔记本电脑', '15.6英寸高性能轻薄本', 6999.00, 50),
('无线鼠标', '人体工学设计，静音点击', 199.00, 200),
('机械键盘', '青轴，RGB背光', 499.00, 100),
('4K显示器', '27英寸IPS屏幕，高色准', 2599.00, 30);

-- 插入一个完整订单
-- 订单1: 张三 购买了 1台笔记本电脑 和 1个无线鼠标
INSERT INTO `orders` (`customer_id`, `status`, `total_amount`) VALUES (1, 'shipped', 7198.00);
SET @last_order_id = LAST_INSERT_ID();
INSERT INTO `order_items` (`order_id`, `product_id`, `quantity`, `price_per_unit`) VALUES
(@last_order_id, 1, 1, 6999.00),
(@last_order_id, 2, 1, 199.00);

-- 订单2: 李四 购买了 2个机械键盘
INSERT INTO `orders` (`customer_id`, `status`, `total_amount`) VALUES (2, 'pending', 998.00);
SET @last_order_id = LAST_INSERT_ID();
INSERT INTO `order_items` (`order_id`, `product_id`, `quantity`, `price_per_unit`) VALUES
(@last_order_id, 3, 2, 499.00);
