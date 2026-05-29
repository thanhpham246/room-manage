from fastapi import HTTPException

from app.services.errors import DomainError


def raise_http_error(error: DomainError) -> None:
    raise HTTPException(status_code=error.status_code, detail=str(error))
