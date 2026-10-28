"""公共依赖项：数据库会话 + 获取当前登录用户"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_access_token

# 从请求头 Authorization: Bearer {token} 中提取 token
# auto_error=False：缺少 / 格式错误的请求头由我们自己返回 401
bearer_scheme = HTTPBearer(auto_error=False)

DBSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    db: DBSession,
) -> User:
    """解析 token → 查询用户；未登录 / token 失效统一返回 401"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录或登录已失效，请先登录",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


# 依赖别名：路由里直接声明 current_user: CurrentUser 即可
CurrentUser = Annotated[User, Depends(get_current_user)]
