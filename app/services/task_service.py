from datetime import datetime
from typing import Protocol

from app.core.exceptions import NotFoundException


class TaskRepositoryProtocol(Protocol):
    def create(self, *, owner_id: int, title: str, description: str | None,
               status, priority, due_date: datetime | None):
        ...

    def get_by_id(self, task_id: int):
        ...

    def list(self, *, owner_id: int, limit: int, offset: int,
             status, priority, search: str | None):
        ...

    def update(self, task):
        ...

    def delete(self, task) -> None:
        ...


class TaskService:
    def __init__(self, repository: TaskRepositoryProtocol) -> None:
        self.repository = repository

    def create(self, *, owner_id: int, title: str, description: str | None,
               status, priority, due_date: datetime | None):
        return self.repository.create(
            owner_id=owner_id,
            title=title.strip(),
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
        )

    def list(self, *, owner_id: int, limit: int, offset: int,
             status=None, priority=None, search: str | None = None):
        return self.repository.list(
            owner_id=owner_id,
            limit=limit,
            offset=offset,
            status=status,
            priority=priority,
            search=search.strip() if search else None,
        )

    def get(self, *, task_id: int, owner_id: int):
        task = self.repository.get_by_id(task_id)
        if task is None or task.owner_id != owner_id:
            raise NotFoundException("Task not found")
        return task

    def update(self, *, task_id: int, owner_id: int, updates: dict):
        task = self.get(task_id=task_id, owner_id=owner_id)
        for field, value in updates.items():
            if value is not None or field in {"description", "due_date"}:
                setattr(task, field, value)
        return self.repository.update(task)

    def delete(self, *, task_id: int, owner_id: int) -> None:
        task = self.get(task_id=task_id, owner_id=owner_id)
        self.repository.delete(task)
