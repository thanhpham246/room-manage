class DomainError(Exception):
    status_code = 400


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class AuthenticationError(DomainError):
    status_code = 401
