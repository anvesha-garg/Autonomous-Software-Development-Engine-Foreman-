import uuid
import asyncio
import logging
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db, ProjectRepository, AsyncSessionLocal
from app.core.ws_manager import ws_manager
from app.core.orchestrator import OrchestratorStateMachine
from app.core.sandbox import SandboxManager
from app.core.config import settings
from app.agents.agent_suite import AgentSuite
from app.models.schemas import TaskStatus, AgentRole

logger = logging.getLogger("api_routes")
router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory store for global workspace file state per project
PROJECT_WORKSPACES: Dict[str, Dict[str, str]] = {}


class CreateProjectRequest(BaseModel):
    name: Optional[str] = "New Project"
    spec: Optional[str] = None
    prompt: Optional[str] = None

    @property
    def get_specification(self) -> str:
        return self.spec or self.prompt or ""


def get_agent_suite(sandbox: SandboxManager) -> AgentSuite:
    """
    Helper to instantiate AgentSuite reading directly from environment variables.
    Falls back to settings if OPENAI_API_KEY environment variable is missing.
    """
    api_key = os.getenv("OPENAI_API_KEY", getattr(settings, "OPENAI_API_KEY", ""))
    return AgentSuite(api_key=api_key, sandbox=sandbox)


async def run_execution_loop(project_id: str) -> None:
    """
    Background worker loop that manages the deterministic dispatch of task graph nodes.
    """
    sandbox = SandboxManager(settings.DOCKER_SANDBOX_IMAGE)
    agents = get_agent_suite(sandbox)

    if project_id not in PROJECT_WORKSPACES:
        PROJECT_WORKSPACES[project_id] = {}

    while True:
        async with AsyncSessionLocal() as session:
            graph = await ProjectRepository.get_graph(session, project_id)
            if not graph:
                break

            state_machine = OrchestratorStateMachine(graph)

            # 1. Update pending -> ready transitions
            newly_ready = state_machine.update_node_statuses()
            if newly_ready:
                await ProjectRepository.update_graph(session, project_id, graph)
                await ws_manager.broadcast(
                    project_id,
                    {
                        "event_type": "GRAPH_UPDATED",
                        "graph": graph.model_dump(),
                    },
                )

            # 2. Check for ready nodes to dispatch
            ready_nodes = [
                n for n in graph.nodes.values() if n.status == TaskStatus.READY
            ]

            if not ready_nodes and state_machine.is_terminal():
                await ws_manager.broadcast(
                    project_id,
                    {
                        "event_type": "SYSTEM_LOG",
                        "message": "Execution finished! All tasks reached terminal state.",
                    },
                )
                break

            # Process ready nodes asynchronously
            for node in ready_nodes:
                node.status = TaskStatus.RUNNING
                await ProjectRepository.update_graph(session, project_id, graph)
                await ws_manager.broadcast(
                    project_id,
                    {
                        "event_type": "NODE_STATUS_CHANGED",
                        "task_id": node.task_id,
                        "status": node.status,
                    },
                )

                # Dispatch worker agent based on role
                try:
                    if node.assigned_agent == AgentRole.CODER:
                        await ws_manager.broadcast(
                            project_id,
                            {
                                "event_type": "AGENT_LOG",
                                "task_id": node.task_id,
                                "agent": "coder",
                                "message": f"Coder starting on task: {node.description}",
                            },
                        )
                        files = await agents.run_coder(
                            node, PROJECT_WORKSPACES[project_id]
                        )
                        PROJECT_WORKSPACES[project_id].update(files)
                        node.artifacts.files_touched = list(files.keys())
                        node.artifacts.diff = "\n".join(
                            [f"--- {k} ---\n{v}" for k, v in files.items()]
                        )

                    # Automatically hand over to Tester agent
                    await ws_manager.broadcast(
                        project_id,
                        {
                            "event_type": "AGENT_LOG",
                            "task_id": node.task_id,
                            "agent": "tester",
                            "message": "Tester running unit tests in isolated Docker sandbox...",
                        },
                    )
                    passed, test_output = await agents.run_tester(
                        node, PROJECT_WORKSPACES[project_id]
                    )
                    node.artifacts.test_output = test_output

                    if passed:
                        # Hand over to Reviewer agent
                        approved, review_notes = await agents.run_reviewer(
                            node, PROJECT_WORKSPACES[project_id], test_output
                        )
                        node.artifacts.review_notes = review_notes

                        if approved:
                            node.status = TaskStatus.PASSED
                            await ws_manager.broadcast(
                                project_id,
                                {
                                    "event_type": "AGENT_LOG",
                                    "task_id": node.task_id,
                                    "agent": "reviewer",
                                    "message": f"Reviewer APPROVED task. Notes: {review_notes}",
                                },
                            )
                        else:
                            next_status = state_machine.handle_node_failure(
                                node.task_id,
                                f"Reviewer requested changes: {review_notes}",
                            )
                            if next_status == TaskStatus.REPLANNING:
                                state_machine.apply_cascading_invalidation(
                                    node.task_id
                                )
                    else:
                        next_status = state_machine.handle_node_failure(
                            node.task_id, f"Tests Failed:\n{test_output}"
                        )
                        if next_status == TaskStatus.REPLANNING:
                            state_machine.apply_cascading_invalidation(
                                node.task_id
                            )

                except Exception as e:
                    logger.error(f"Error processing node {node.task_id}: {e}")
                    state_machine.handle_node_failure(node.task_id, str(e))

                # Save updated graph state & notify frontend
                await ProjectRepository.update_graph(session, project_id, graph)
                await ws_manager.broadcast(
                    project_id,
                    {
                        "event_type": "GRAPH_UPDATED",
                        "graph": graph.model_dump(),
                    },
                )

        await asyncio.sleep(2)  # Poll delay between state machine iterations


# --- Endpoint Handlers ---


@router.post("", response_model=Dict[str, Any])
async def create_project(
    req: CreateProjectRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """POST /projects — Creates project from plain text spec & invokes Planner."""
    specification = req.get_specification
    if not specification:
        raise HTTPException(
            status_code=422,
            detail="Either 'spec' or 'prompt' field must be provided.",
        )

    project_id = str(uuid.uuid4())
    sandbox = SandboxManager(settings.DOCKER_SANDBOX_IMAGE)
    agents = get_agent_suite(sandbox)

    # 1. Planner generates initial self-critiqued task graph
    graph = await agents.run_planner(project_id, specification)

    # 2. Persist project state
    await ProjectRepository.save_project(
        db, project_id, req.name or "New Project", specification, graph
    )

    # 3. Trigger orchestrator state loop in background
    background_tasks.add_task(run_execution_loop, project_id)

    return {
        "project_id": project_id,
        "name": req.name or "New Project",
        "status": "active",
        "graph": graph.model_dump(),
    }


@router.get("/{project_id}/graph", response_model=Dict[str, Any])
async def get_project_graph(project_id: str, db: AsyncSession = Depends(get_db)):
    """GET /projects/:id/graph — Fetch current task graph state."""
    graph = await ProjectRepository.get_graph(db, project_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Project not found")
    return graph.model_dump()


@router.get("/{project_id}/artifacts", response_model=Dict[str, Any])
async def get_project_artifacts(
    project_id: str, db: AsyncSession = Depends(get_db)
):
    """GET /projects/:id/artifacts — Fetch generated code diffs, logs, and review notes."""
    graph = await ProjectRepository.get_graph(db, project_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Project not found")

    artifacts = {}
    for node_id, node in graph.nodes.items():
        artifacts[node_id] = node.artifacts.model_dump()

    return {
        "project_id": project_id,
        "workspace_files": PROJECT_WORKSPACES.get(project_id, {}),
        "node_artifacts": artifacts,
    }


@router.post("/{project_id}/nodes/{node_id}/retry")
async def retry_node(
    project_id: str, node_id: str, db: AsyncSession = Depends(get_db)
):
    """POST /projects/:id/nodes/:id/retry — Manual retry trigger for a failed/blocked node."""
    graph = await ProjectRepository.get_graph(db, project_id)
    if not graph or node_id not in graph.nodes:
        raise HTTPException(status_code=404, detail="Task node not found")

    node = graph.nodes[node_id]
    node.status = TaskStatus.READY
    node.attempts = 0
    await ProjectRepository.update_graph(db, project_id, graph)

    await ws_manager.broadcast(
        project_id,
        {"event_type": "GRAPH_UPDATED", "graph": graph.model_dump()},
    )
    return {"message": f"Node {node_id} reset to READY"}


@router.websocket("/{project_id}/stream")
async def project_stream(websocket: WebSocket, project_id: str):
    """GET /projects/:id/stream — WebSocket connection for live log & node status updates."""
    await ws_manager.connect(project_id, websocket)
    try:
        while True:
            # Keep socket alive and handle incoming user interaction events if needed
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(project_id, websocket)