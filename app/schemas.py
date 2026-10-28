"""Pydantic 请求 / 响应模型（校验层）"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==================== 用户模块 ====================
class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, examples=["testuser"])
    email: EmailStr = Field(examples=["test@qq.com"])
    password: str = Field(min_length=6, max_length=50, examples=["123456"])


class UserLoginRequest(BaseModel):
    username: str = Field(examples=["testuser"])
    password: str = Field(examples=["123456"])


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==================== 分类模块 ====================
class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50, examples=["Python"])


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


# ==================== 文章模块 ====================
class ArticleCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200, examples=["我的第一篇文章"])
    content: str = Field(min_length=1, examples=["Hello World"])
    category_id: Optional[int] = None


class ArticleUpdateRequest(BaseModel):
    """部分更新：只传需要修改的字段"""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = Field(default=None, min_length=1)
    category_id: Optional[int] = None


class AuthorBrief(BaseModel):
    """嵌套的作者信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class CategoryBrief(BaseModel):
    """嵌套的分类信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ArticleResponse(BaseModel):
    """文章详情响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    author: AuthorBrief
    category: Optional[CategoryBrief] = None
    created_at: datetime
    updated_at: datetime


class ArticleListItem(BaseModel):
    """文章列表项（不含正文，减少传输量）"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: AuthorBrief
    category: Optional[CategoryBrief] = None
    created_at: datetime


class ArticlePageResponse(BaseModel):
    """文章分页响应：offset + limit，返回 total 总数"""

    total: int
    page: int
    size: int
    items: list[ArticleListItem]


# ==================== 评论模块 ====================
class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=500, examples=["好文章！"])


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    # ORM 关系名为 user，对外统一输出为 author（与文章接口的 author 字段保持一致）
    author: AuthorBrief = Field(validation_alias="user")
    created_at: datetime


class CommentPageResponse(BaseModel):
    total: int
    items: list[CommentResponse]
