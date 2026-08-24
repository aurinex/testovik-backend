from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from ..database import results as results_col
from ..database import tasks as tasks_col
from ..dependencies import get_current_user
from ..models import Result, Task, User
from ..schemas import ResultOut, ResultSubmit
from ..scoring import score_task

router = APIRouter(prefix="/api/results", tags=["results"])


@router.post("", response_model=ResultOut)
async def submit_result(body: ResultSubmit, user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(body.task_id):
        raise HTTPException(status_code=404, detail="Задание не найдено")
    doc = await tasks_col.find_one({"_id": ObjectId(body.task_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    task = Task(**doc)
    raw_answers = [a.payload for a in body.answers]
    correct, total, details = score_task(task.task_type, task.content, raw_answers)

    max_score = task.points
    score = round(max_score * (correct / total)) if total else 0

    result = Result(
        user_id=str(user.id),
        task_id=str(task.id),
        task_title=task.title,
        task_type=task.task_type,
        topic=task.topic,
        score=score,
        max_score=max_score,
        correct_count=correct,
        total_count=total,
        answers=details,
    )
    inserted = await results_col.insert_one(result.model_dump(exclude={"id"}))
    result.id = str(inserted.inserted_id)
    return ResultOut(**result.model_dump())


@router.get("/me", response_model=list[ResultOut])
async def my_results(user: User = Depends(get_current_user)):
    docs = await results_col.find({"user_id": str(user.id)}).sort("completed_at", -1).to_list(1000)
    return [ResultOut(**Result(**d).model_dump()) for d in docs]