from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_task_service
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user=Depends(get_current_user),
) -> object:
    return service.create(
        owner_id=current_user.id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
    )


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user=Depends(get_current_user),
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    search: str | None = None,
) -> list[object]:
    return service.list(
        owner_id=current_user.id,
        limit=limit,
        offset=offset,
        status=status,
        priority=priority,
        search=search,
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user=Depends(get_current_user),
) -> object:
    return service.get(task_id=task_id, owner_id=current_user.id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user=Depends(get_current_user),
) -> object:
    return service.update(
        task_id=task_id,
        owner_id=current_user.id,
        updates=payload.model_dump(exclude_unset=True),
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user=Depends(get_current_user),
) -> None:
    service.delete(task_id=task_id, owner_id=current_user.id)
