# 个人博客系统 Web API

基于 **FastAPI** 开发的个人博客后端服务，提供用户、分类、文章、评论的 RESTful 接口，支持 JWT 登录鉴权、文章分页与分类筛选。

## 项目简介

本项目是一个前后端分离的个人博客系统后端，采用分层设计（路由层 / 模型层 / 校验层），实现了完整的用户认证、文章管理与评论功能，共提供 **12 个 RESTful 接口**。

## 技术栈

| 技术 | 用途 |
| --- | --- |
| Python 3.10+ | 开发语言 |
| FastAPI | Web 框架 |
| Uvicorn | ASGI 服务器 |
| SQLAlchemy 2.0 | ORM 框架 |
| MySQL 8.0 | 数据库 |
| PyMySQL | MySQL 驱动 |
| python-jose | JWT 生成与校验 |
| passlib[bcrypt] | 密码加密 |
| Postman | 接口测试 |

## 功能模块

- **用户模块**：注册、登录（JWT）、获取当前用户信息
- **分类模块**：新增分类、分类列表
- **文章模块**：发布、列表（分页/筛选）、详情、修改、删除
- **评论模块**：发表评论、评论列表

## 项目结构

```
blog_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # 入口，注册路由
│   ├── database.py          # 数据库连接
│   ├── models.py            # ORM 模型
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── security.py          # 密码加密 + JWT
│   ├── deps.py              # 依赖项（获取当前用户）
│   └── routers/
│       ├── users.py         # 用户接口
│       ├── categories.py    # 分类接口
│       ├── articles.py      # 文章接口
│       └── comments.py      # 评论接口
├── sql/
│   └── init.sql             # 建库建表 SQL（4 张表）
├── postman/
│   └── blog_api.postman_collection.json   # Postman 测试集合
├── requirements.txt
├── .gitignore
└── README.md
```

## 数据库设计

共 4 张表：`user` / `category` / `article` / `comment`

关联关系：

- `user 1 → N article`（一个用户可发多篇文章）
- `category 1 → N article`（一个分类下有多篇文章）
- `article 1 → N comment`（一篇文章有多条评论）

外键级联策略：

- 删除文章 → **级联删除**其所有评论（CASCADE）
- 删除分类 → 文章保留，`category_id` 置空（SET NULL）

建表 SQL 见 [`sql/init.sql`](./sql/init.sql)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/08212007/blog_api.git
cd blog_api
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows 激活
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

在 MySQL 中执行 `sql/init.sql`，创建数据库 `blog_db` 与 4 张数据表：

```bash
mysql -uroot -p < sql/init.sql
```

### 5. 修改数据库配置

编辑 `app/database.py`，将 `DB_PASSWORD` 改为你的 MySQL 密码：

```python
DB_USER = "root"
DB_PASSWORD = "你的密码"
```

### 6. 启动服务

```bash
uvicorn app.main:app --reload
```

启动后访问：

- **博客演示页面**：http://127.0.0.1:8000 （简单前端，调用本项目 API）
- **接口文档（Swagger UI）**：http://127.0.0.1:8000/docs （本地加载不依赖 CDN）
- 备用接口文档（Scalar）：http://127.0.0.1:8000/scalar

## 接口说明

| # | 方法 | 路径 | 说明 | 需登录 |
| --- | --- | --- | --- | --- |
| 1 | POST | `/users/register` | 用户注册 | ❌ |
| 2 | POST | `/users/login` | 用户登录 | ❌ |
| 3 | GET | `/users/me` | 当前用户信息 | ✅ |
| 4 | POST | `/categories` | 新增分类 | ✅ |
| 5 | GET | `/categories` | 分类列表 | ❌ |
| 6 | POST | `/articles` | 发布文章 | ✅ |
| 7 | GET | `/articles` | 文章列表（分页/筛选） | ❌ |
| 8 | GET | `/articles/{id}` | 文章详情 | ❌ |
| 9 | PUT | `/articles/{id}` | 修改文章 | ✅ |
| 10 | DELETE | `/articles/{id}` | 删除文章 | ✅ |
| 11 | POST | `/articles/{id}/comments` | 发表评论 | ✅ |
| 12 | GET | `/articles/{id}/comments` | 评论列表 | ❌ |

### 鉴权说明

需登录的接口，请在请求头中携带 token：

```
Authorization: Bearer {access_token}
```

未登录访问敏感接口返回 **401**；修改/删除他人文章返回 **403**。

## 使用示例

### 1. 注册用户

```bash
curl -X POST http://127.0.0.1:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "123456", "email": "test@qq.com"}'
```

### 2. 登录获取 token

```bash
curl -X POST http://127.0.0.1:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "123456"}'
```

### 3. 发布文章（带 token）

```bash
curl -X POST http://127.0.0.1:8000/articles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {你的token}" \
  -d '{"title": "我的第一篇文章", "content": "Hello World", "category_id": 1}'
```

### 4. 分页获取文章列表

```bash
curl "http://127.0.0.1:8000/articles?page=1&size=10&category_id=1"
```

## 接口测试（Postman）

1. 打开 Postman → **Import** → 选择 `postman/blog_api.postman_collection.json`
2. 先执行「用户模块 → 用户登录」，测试脚本会**自动把 token 存入集合变量**
3. 依次执行其余接口，需要鉴权的接口会自动带上 `Authorization: Bearer {{token}}`

也可以直接在浏览器打开 http://127.0.0.1:8000/docs ，用 Swagger 文档在线调试。

## 开发笔记

- 密码使用 `bcrypt` 加密存储，数据库不保存明文
- 使用 JWT 实现无状态鉴权，token 有效期 1 天
- 文章修改 / 删除接口做了**归属校验**，非本人操作返回 403
- 文章列表通过 `offset` + `limit` 实现分页，返回 `total` 总数
- 外键级联：删除文章自动删除其评论，删除分类不影响文章
- MySQL 连接串带 `?charset=utf8mb4`，避免中文乱码

## 后续计划

- [ ] 增加文章点赞与收藏
- [ ] 接入 Redis 缓存热门文章
- [ ] 增加单元测试
- [ ] 使用 Docker 部署

## 作者

**王志元**

- 求职方向：Python 后端开发工程师
- 邮箱：1769809946@qq.com

## License

本项目仅用于学习与技术展示。
