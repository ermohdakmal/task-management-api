from typing import Protocol

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import hash_password, verify_password


class UserRepositoryProtocol(Protocol):
    def get_by_email(self, email: str):
        ...

    def get_by_id(self, user_id: int):
        ...

    def create(self, email: str, hashed_password: str):
        ...


class AuthService:
    def __init__(self, repository: UserRepositoryProtocol) -> None:
        self.repository = repository

    def register(self, email: str, password: str):
        normalized_email = email.strip().lower()
        if self.repository.get_by_email(normalized_email) is not None:
            raise ConflictException("A user with this email already exists")
        return self.repository.create(normalized_email, hash_password(password))

    def authenticate(self, email: str, password: str):
        normalized_email = email.strip().lower()
        user = self.repository.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        return user
