from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    PLANNER = "planner"
    CODER = "coder"
    TESTER = "tester"
    REVIEWER = "reviewer"


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    RETRYING = "retrying"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    FAILED = "failed"


class Artifacts(BaseModel):
    files: Dict[str, str] = Field(default_factory=dict)
    files_touched: List[str] = Field(default_factory=list)
    diff: Optional[str] = None
    test_results: Optional[str] = None
    test_output: Optional[str] = None
    review_notes: Optional[str] = None


class TaskNode(BaseModel):
    task_id: str
    description: str
    assigned_agent: AgentRole
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = Field(default=0)
    max_attempts: int = Field(default=3)
    failure_history: List[Dict[str, Any]] = Field(default_factory=list)
    artifacts: Artifacts = Field(default_factory=Artifacts)


class TaskGraph(BaseModel):
    project_id: str
    nodes: Dict[str, TaskNode] = Field(default_factory=dict)