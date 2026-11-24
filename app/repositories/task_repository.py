from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskPriority, TaskStatus


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, owner_id: int, title: str, description: str | None,
               status: TaskStatus, priority: TaskPriority, due_date: datetime | None) -> Task:
        task = Task(
            owner_id=owner_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def list(
        self,
        *,
        owner_id: int,
        limit: int,
        offset: int,
        status: TaskStatus | None,
        priority: TaskPriority | None,
        search: str | None,
    ) -> list[Task]:
        statement = select(Task).where(Task.owner_id == owner_id)
        if status is not None:
            statement = statement.where(Task.status == status)
        if priority is not None:
            statement = statement.where(Task.priority == priority)
        if search:
            statement = statement.where(Task.title.ilike(f"%{search}%"))
        statement = statement.order_by(Task.created_at.desc(), Task.id.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(statement).all())

    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
