"""应用入口：注册路由"""
from contextlib import asynccontextmanager
from pathlib import Path

import swagger_ui_bundle
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .database import engine
from .models import Base
from .routers import articles, categories, comments, users

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动建表（已存在则跳过）；生产环境建议用 sql/init.sql 手动建表
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="个人博客系统 Web API",
    description="基于 FastAPI 的个人博客后端服务：用户 / 分类 / 文章 / 评论，JWT 鉴权",
    version="1.0.0",
    lifespan=lifespan,
    # 关闭默认文档：默认 /docs 从 jsdelivr CDN 加载资源，国内网络经常加载失败
    docs_url=None,
    redoc_url=None,
)

# FastAPI 默认输出 OpenAPI 3.1.0，降到 3.0.2 以获得最好的文档工具兼容性
app.openapi_version = "3.0.2"

# ---------- 静态资源 ----------
# 项目静态资源（演示页面 index.html、Scalar 资源等）
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

# Swagger UI 资源（/docs 用，来自 swagger-ui-bundle 包，本地化不依赖 CDN）
_pkg_dir = Path(swagger_ui_bundle.__file__).parent
SWAGGER_UI_DIR = next(_pkg_dir.rglob("swagger-ui-bundle.js")).parent
app.mount("/swagger-ui", StaticFiles(directory=str(SWAGGER_UI_DIR)), name="swagger-ui")


@app.get("/docs", include_in_schema=False)
async def swagger_docs():
    """主文档：Swagger UI（最常见的接口文档界面）"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/swagger-ui/swagger-ui.css",
    )


# Scalar standalone.js 有 4.6MB，未提交到 Git 仓库；
# 本地存在该文件则用本地（离线可用），否则回退 CDN
SCALAR_JS_LOCAL = BASE_DIR / "static" / "scalar" / "standalone.js"
SCALAR_JS_URL = (
    "/static/scalar/standalone.js"
    if SCALAR_JS_LOCAL.exists()
    else "https://cdn.jsdelivr.net/npm/@scalar/api-reference"
)


@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    """备用文档：Scalar，界面现代美观"""
    return HTMLResponse(
        content=f"""<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>个人博客系统 Web API - 接口文档</title>
</head>
<body>
    <script
        id="api-reference"
        data-url="/openapi.json"
        data-configuration='{{"theme":"default","layout":"modern","darkMode":false}}'
    ></script>
    <script src="{SCALAR_JS_URL}"></script>
</body>
</html>"""
    )


# 注册路由
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(articles.router)
app.include_router(comments.router)


@app.get("/", include_in_schema=False)
def index():
    """博客首页（演示用前端页面，调用本项目的 API）"""
    # no-cache：演示页面经常改动，避免浏览器缓存旧版本
    return FileResponse(
        BASE_DIR / "static" / "web" / "index.html",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/healthz", tags=["默认"], summary="健康检查")
def healthz():
    return {"message": "个人博客系统 Web API 运行中", "docs": "/docs"}
