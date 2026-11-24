from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.task_service import TaskService

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_task_repository(db: Annotated[Session, Depends(get_db)]) -> TaskRepository:
    return TaskRepository(db)


def get_auth_service(repository: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(repository)


def get_task_service(repository: Annotated[TaskRepository, Depends(get_task_repository)]) -> TaskService:
    return TaskService(repository)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
):
    if credentials is None:
        raise UnauthorizedException("Not authenticated")
    user_id = decode_access_token(credentials.credentials)
    user = repository.get_by_id(int(user_id))
    if user is None:
        raise UnauthorizedException("Could not validate credentials")
    return user
