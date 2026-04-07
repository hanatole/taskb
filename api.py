import json
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, Path, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRouter
from fastapi_pagination import Page, add_pagination, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlmodel import Session, select
from starlette.responses import JSONResponse

from models import Task
from serializers import TaskResponse, TaskRequest
from settings import create_db_and_tables, get_session, logger, engine


class FilterParams(BaseModel):
    status: str | None = None
    priority: str | None = None
    due_date: str | None = None


class PaginationParams(Params):
    size: int = 5
    max_size: int = 25


def seed_database():
    with Session(engine) as session:
        if session.exec(select(Task)).first():
            return
        with open("data.json") as f:
            data = json.load(f)
        session.add_all([Task(**TaskRequest(**item).model_dump(), status="OPEN") for item in data])
        session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    seed_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Task manager API",
    description="Simple task manager API",
    version="1.0.0",
    redoc_url="/api/v1/redoc",
    docs_url="/api/v1/docs",
)

add_pagination(app)
router = APIRouter(prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    if exc.errors()[0]["input"] is None:
        detail = "body: Body required"
    else:
        detail = f"{exc.errors()[0]['loc'][1]}: {exc.errors()[0]['msg']}"
    logger.error(detail)
    return JSONResponse(status_code=400, content={"detail": detail})


@router.get("/healthcheck", response_model=dict)
async def healthcheck():
    return {"status": "healthy"}


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_todo(
        request: Request,
        response: Response,
        item: TaskRequest,
        session: Session = Depends(get_session),
):
    logger.info(f"Creating new task: {item.title}")
    todo = Task(**item.model_dump(), status="OPEN")
    session.add(todo)
    session.commit()
    session.refresh(todo)
    logger.success("Task created successfully")
    location = request.url_for("get_todo", pk=todo.id)
    response.headers["Location"] = str(location)

    return TaskResponse(**todo.model_dump())


@router.put("/tasks/{pk}", response_model=TaskResponse)
async def update_todo(
        pk: Annotated[int, Path(title="ID of the task")],
        item: TaskRequest,
        session: Session = Depends(get_session),
):
    logger.info(f"Updating task {pk}")
    task = session.get(Task, pk)
    if not task:
        logger.error(f"Task {pk} not found")
        raise HTTPException(status_code=404, detail=f"Task {pk} not found")
    task.title = item.title
    task.description = item.description
    task.due_date = item.due_date
    task.priority = item.priority
    session.commit()
    session.refresh(task)
    logger.success(f"Task {pk} updated successfully")
    return task


@router.get("/tasks/{pk}", response_model=TaskResponse, name="get_todo")
async def get_todo(
        pk: Annotated[int, Path(title="ID of the task")],
        session: Session = Depends(get_session),
):
    logger.info(f"Getting task {pk}")
    response = session.get(Task, pk)
    if response:
        logger.success(f"Task {pk} found successfully")
        return response
    logger.error(f"Task {pk} not found")
    raise HTTPException(status_code=404, detail=f"Task {pk} not found")


@router.get("/tasks", response_model=Page[TaskResponse])
async def get_all(
        q: FilterParams = Depends(),
        pagination: PaginationParams = Depends(),
        session: Session = Depends(get_session),
):
    statement = select(Task)
    if status := q.status:
        statement = statement.where(Task.status == status)
    if priority := q.priority:
        statement = statement.where(Task.priority == priority)
    if due_date := q.due_date:
        if due_date == "PAST":
            statement = statement.where(Task.due_date < date.today())
        elif due_date == "FUTURE":
            statement = statement.where(Task.due_date > date.today())
        else:
            statement = statement.where(Task.due_date == date.today())

    statement = statement.order_by(Task.due_date)
    return paginate(session, statement, pagination)


@router.post("/tasks/{pk}", response_model=TaskResponse)
async def complete_todo(
        pk: Annotated[int, Path(title="ID of the task")],
        session: Session = Depends(get_session),
):
    logger.info(f"Marking task {pk} as completed")
    task = session.get(Task, pk)
    if not task:
        logger.error(f"Task {pk} not found")
        raise HTTPException(status_code=404, detail=f"Task {pk} not found")
    task.status = "COMPLETED"
    session.commit()
    session.refresh(task)
    logger.success(f"Task {pk} marked as completed successfully")
    return task


@router.delete("/tasks/{pk}", response_model=None, status_code=204)
async def delete_todo(
        pk: Annotated[int, Path(title="ID of the task")],
        session: Session = Depends(get_session),
):
    logger.info(f"Deleting task {pk}")
    task = session.get(Task, pk)
    if not task:
        logger.error(f"Task {pk} not found")
        raise HTTPException(status_code=404, detail=f"Task {pk} not found")
    session.delete(task)
    session.commit()
    logger.success(f"Task {pk} deleted successfully")
    return None


app.include_router(router)
