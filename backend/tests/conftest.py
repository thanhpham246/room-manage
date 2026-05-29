import os
from collections.abc import AsyncGenerator, Generator

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["ROOM_MANAGE_ENVIRONMENT"] = "test"
os.environ["ROOM_MANAGE_PASSWORD_HASH_ROUNDS"] = "4"

from app.core.security import hash_password
from app.db.base import Base
from app.dependencies.database import get_db
from app.main import create_app
from app.models import User


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        admin = User(
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=hash_password("password123"),
            role="admin",
        )
        session.add(admin)
        session.commit()
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
async def client(db_session: Session) -> AsyncGenerator[httpx.AsyncClient, None]:
    app = create_app()

    async def override_get_db() -> AsyncGenerator[Session, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
async def authenticated_client(client: httpx.AsyncClient) -> httpx.AsyncClient:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    return client
