"""分类模块接口：新增分类 / 分类列表"""
from fastapi import APIRouter, HTTPException, status

from ..deps import CurrentUser, DBSession
from ..models import Category
from ..schemas import CategoryCreateRequest, CategoryResponse

router = APIRouter(prefix="/categories", tags=["分类模块"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增分类",
)
def create_category(request: CategoryCreateRequest, db: DBSession, current_user: CurrentUser):
    # 同名分类不允许重复
    exists = db.query(Category).filter(Category.name == request.name).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="分类已存在"
        )

    category = Category(name=request.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get(
    "",
    response_model=list[CategoryResponse],
    summary="分类列表",
)
def list_categories(db: DBSession):
    return db.query(Category).order_by(Category.id).all()
