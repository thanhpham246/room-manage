from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories.users import UserRepository
from app.schemas.users import UserCreate
from app.services.errors import AuthenticationError, ConflictError


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("Inactive user")
        return user

    def create_token(self, user: User) -> str:
        return create_access_token(str(user.id))

    def create_user(self, payload: UserCreate) -> User:
        if self.users.get_by_email(payload.email):
            raise ConflictError("Email already exists")
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        return self.users.create(user)
