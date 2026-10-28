"""评论模块接口：发表评论 / 评论列表"""
from fastapi import APIRouter, HTTPException, status

from ..deps import CurrentUser, DBSession
from ..models import Article, Comment
from ..schemas import CommentCreateRequest, CommentPageResponse, CommentResponse

router = APIRouter(prefix="/articles/{article_id}/comments", tags=["评论模块"])


def _get_article_or_404(article_id: int, db: DBSession) -> Article:
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在"
        )
    return article


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="发表评论",
)
def create_comment(
    article_id: int, request: CommentCreateRequest, db: DBSession, current_user: CurrentUser
):
    _get_article_or_404(article_id, db)

    comment = Comment(
        content=request.content,
        article_id=article_id,
        user_id=current_user.id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("", response_model=CommentPageResponse, summary="评论列表")
def list_comments(article_id: int, db: DBSession):
    _get_article_or_404(article_id, db)

    query = db.query(Comment).filter(Comment.article_id == article_id)
    total = query.count()
    items = query.order_by(Comment.created_at.desc(), Comment.id.desc()).all()
    return CommentPageResponse(total=total, items=items)
