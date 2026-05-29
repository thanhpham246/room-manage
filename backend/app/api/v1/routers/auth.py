from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.v1.routers._errors import raise_http_error
from app.core.config import get_settings
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models import User
from app.repositories.users import UserRepository
from app.schemas.users import UserLogin, UserRead
from app.services.auth import AuthService
from app.services.errors import DomainError

router = APIRouter()


@router.post("/login", response_model=UserRead)
async def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)) -> User:
    settings = get_settings()
    service = AuthService(UserRepository(db))
    try:
        user = service.authenticate(payload.email, payload.password)
    except DomainError as error:
        raise_http_error(error)
    token = service.create_token(user)
    response.set_cookie(
        key=settings.access_token_cookie_name,
        value=token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        secure=settings.cookie_secure,
        samesite="lax",
    )
    return user


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    settings = get_settings()
    response.delete_cookie(settings.access_token_cookie_name)
    return {"status": "ok"}


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
