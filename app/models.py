"""ORM 模型：user / category / article / comment 四张表"""
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    """用户表"""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(100), nullable=False)  # bcrypt 加密，不存明文
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    articles = relationship("Article", back_populates="author")
    comments = relationship("Comment", back_populates="user")


class Category(Base):
    """分类表"""

    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    articles = relationship("Article", back_populates="category")


class Article(Base):
    """文章表（核心表）：外键关联 user、category"""

    __tablename__ = "article"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    # 删除用户 → 级联删除其文章
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    # 删除分类 → 文章保留，category_id 置空（SET NULL）
    category_id = Column(Integer, ForeignKey("category.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    # ORM 级删除评论（数据库层还有 ON DELETE CASCADE 兜底）
    comments = relationship(
        "Comment", back_populates="article", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_article_user_category", "user_id", "category_id"),)


class Comment(Base):
    """评论表：外键关联 article、user"""

    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500), nullable=False)
    # 删除文章 → 级联删除其评论
    article_id = Column(
        Integer, ForeignKey("article.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    article = relationship("Article", back_populates="comments")
    user = relationship("User", back_populates="comments")
