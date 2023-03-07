from fastapi import status, Depends, APIRouter, HTTPException

from common import oauth2
from common.redis import parsing_task
from schemas.parsing_task_schema import ParsingTask

router = APIRouter(
    prefix="/parser"
)


@router.post("/run/", status_code=status.HTTP_201_CREATED, tags=["Run Parser"])
async def run_parser(validation=Depends(oauth2.validate_user)):
    # Before starting new parsing task check if previous one not running.
    task_status = await parsing_task.get_status()
    if task_status in ('active', 'in_progress'):
        task_id = await parsing_task.get_task_id()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Task {task_id} is already running")

    task_id = await parsing_task.start()
    return {"task_id": task_id}


@router.get("/status/", response_model=ParsingTask, tags=["Get Parsing Status"])
async def get_parsing_task_status(validation=Depends(oauth2.validate_user)):
    task = await parsing_task.get_task()
    return task
