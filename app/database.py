"""数据库连接配置"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------- MySQL 连接配置（改成你自己的密码） ----------
DB_USER = "root"
DB_PASSWORD = "123456"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "blog_db"

DEFAULT_MYSQL_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# 优先读取环境变量 DATABASE_URL，方便切换数据库（如本地测试用 SQLite）
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_MYSQL_URL)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # 取连接前先 ping，防止 MySQL 长连接失效
    pool_recycle=3600,    # 每小时回收连接
    echo=False,           # True 时在控制台打印 SQL，便于调试
)

# 会话工厂：每个请求创建一个会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 模型基类
Base = declarative_base()


def get_db():
    """FastAPI 依赖：每个请求获取一个数据库会话，请求结束后自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
