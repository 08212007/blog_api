"""用户模块接口：注册 / 登录 / 当前用户"""
from fastapi import APIRouter, HTTPException, status

from ..deps import CurrentUser, DBSession
from ..models import User
from ..schemas import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/users", tags=["用户模块"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
)
def register(request: UserRegisterRequest, db: DBSession):
    # 1. 校验用户名 / 邮箱是否已被注册
    exists = (
        db.query(User)
        .filter((User.username == request.username) | (User.email == request.email))
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或邮箱已被注册"
        )

    # 2. bcrypt 加密密码后入库，不存明文
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse, summary="用户登录")
def login(request: UserLoginRequest, db: DBSession):
    # 1. 查用户 + 校验密码
    user = db.query(User).filter(User.username == request.username).first()
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误"
        )

    # 2. 签发 JWT
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse, summary="当前用户信息")
def me(current_user: CurrentUser):
    """依赖 get_current_user 完成鉴权，未登录返回 401"""
    return current_user
