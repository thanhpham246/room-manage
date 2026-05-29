from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.routers._errors import raise_http_error
from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.models import User
from app.repositories.users import UserRepository
from app.schemas.users import UserCreate, UserRead
from app.services.auth import AuthService
from app.services.errors import DomainError

router = APIRouter(dependencies=[Depends(require_roles("admin"))])


@router.get("", response_model=list[UserRead])
async def list_users(db: Session = Depends(get_db)) -> list[User]:
    return UserRepository(db).list()


@router.post("", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    try:
        return AuthService(UserRepository(db)).create_user(payload)
    except DomainError as error:
        raise_http_error(error)
