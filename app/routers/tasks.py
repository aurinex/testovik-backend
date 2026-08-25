from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from ..database import tasks as tasks_col
from ..dependencies import get_current_user
from ..models import Task, User
from ..schemas import TaskFullOut, TaskOut

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _task_out(t: Task) -> TaskOut:
    return TaskOut(**t.model_dump())


@router.get("", response_model=list[TaskOut])
async def list_tasks(user: User = Depends(get_current_user)):
    # Фильтр по возрастной группе
    age_filter = {"age_groups": user.age_group}
    
    # Фильтр по группам пользователя
    if user.groups:
        group_filter = {
             "$or": [
                {"forbidden_groups": {"$size": 0}},
                {"forbidden_groups": {"$not": {"$in": user.groups}}}
            ]
        }
    else:
        # Если у пользователя нет групп — показываем только задания без ограничений
        forbidden_filter = {}
    
    query = {"$and": [age_filter, forbidden_filter]}
    
    tasks = await tasks_col.find(query).sort("order", 1).to_list(1000)
    return [_task_out(Task(**t)) for t in tasks]


@router.get("/{task_id}", response_model=TaskFullOut)
async def get_task(task_id: str, user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=404, detail="Задание не найдено")
    doc = await tasks_col.find_one({"_id": ObjectId(task_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    task = Task(**doc)
    
    # Проверка возрастной группы
    if user.age_group not in task.age_groups and "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Задание не доступно для вашей возрастной группы")
    
    # Проверка групп
    if task.forbidden_groups and "admin" not in user.roles:
        if any(g in user.groups for g in task.forbidden_groups):
            raise HTTPException(status_code=403, detail="Задание запрещено для вашей группы")

    return TaskFullOut(**task.model_dump())