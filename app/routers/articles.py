"""文章模块接口：发布 / 列表（分页筛选）/ 详情 / 修改 / 删除"""
from fastapi import APIRouter, HTTPException, Query, status

from ..deps import CurrentUser, DBSession
from ..models import Article, Category
from ..schemas import (
    ArticleCreateRequest,
    ArticlePageResponse,
    ArticleResponse,
    ArticleUpdateRequest,
)

router = APIRouter(prefix="/articles", tags=["文章模块"])


def _get_owned_article(article_id: int, db: DBSession, current_user: CurrentUser) -> Article:
    """获取文章并做归属校验：不存在 → 404；非本人 → 403"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在"
        )
    if article.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权限操作他人文章"
        )
    return article


def _check_category_exists(category_id: int, db: DBSession) -> None:
    """校验分类是否存在，不存在 → 400"""
    if db.query(Category).filter(Category.id == category_id).first() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="分类不存在"
        )


@router.post(
    "",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="发布文章",
)
def create_article(request: ArticleCreateRequest, db: DBSession, current_user: CurrentUser):
    if request.category_id is not None:
        _check_category_exists(request.category_id, db)

    article = Article(
        title=request.title,
        content=request.content,
        user_id=current_user.id,
        category_id=request.category_id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.get("", response_model=ArticlePageResponse, summary="文章列表（分页/筛选）")
def list_articles(
    db: DBSession,
    page: int = Query(default=1, ge=1, description="页码，从 1 开始"),
    size: int = Query(default=10, ge=1, le=50, description="每页条数，最大 50"),
    category_id: int | None = Query(default=None, description="按分类筛选"),
):
    query = db.query(Article)
    if category_id is not None:
        query = query.filter(Article.category_id == category_id)

    # offset + limit 分页，并返回 total 总数
    total = query.count()
    items = (
        query.order_by(Article.created_at.desc(), Article.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return ArticlePageResponse(total=total, page=page, size=size, items=items)


@router.get("/{article_id}", response_model=ArticleResponse, summary="文章详情")
def get_article(article_id: int, db: DBSession):
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在"
        )
    return article


@router.put("/{article_id}", response_model=ArticleResponse, summary="修改文章")
def update_article(
    article_id: int,
    request: ArticleUpdateRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    # 只有作者本人能修改，否则 403
    article = _get_owned_article(article_id, db, current_user)

    if request.category_id is not None:
        _check_category_exists(request.category_id, db)

    # 部分更新：只改传入的字段
    if request.title is not None:
        article.title = request.title
    if request.content is not None:
        article.content = request.content
    if request.category_id is not None:
        article.category_id = request.category_id

    db.commit()
    db.refresh(article)
    return article


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除文章",
)
def delete_article(article_id: int, db: DBSession, current_user: CurrentUser):
    # 只有作者本人能删除，否则 403；删除后其评论级联删除
    article = _get_owned_article(article_id, db, current_user)
    db.delete(article)
    db.commit()
