import json
from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, func
from app.core.config import settings
from app.models.schemas import TaskGraph

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    spec: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="planning")
    graph_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

class ProjectRepository:
    @staticmethod
    async def save_project(session: AsyncSession, project_id: str, name: str, spec: str, graph: TaskGraph) -> ProjectModel:
        db_project = ProjectModel(
            id=project_id,
            name=name,
            spec=spec,
            status="active",
            graph_json=graph.model_dump_json()
        )
        session.add(db_project)
        await session.commit()
        return db_project

    @staticmethod
    async def get_graph(session: AsyncSession, project_id: str) -> Optional[TaskGraph]:
        db_project = await session.get(ProjectModel, project_id)
        if not db_project:
            return None
        data = json.loads(db_project.graph_json)
        return TaskGraph(**data)

    @staticmethod
    async def update_graph(session: AsyncSession, project_id: str, graph: TaskGraph) -> None:
        db_project = await session.get(ProjectModel, project_id)
        if db_project:
            db_project.graph_json = graph.model_dump_json()
            await session.commit()