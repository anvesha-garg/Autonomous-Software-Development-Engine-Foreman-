import asyncio
import logging
from typing import List, Set, Dict, Optional
from app.models.schemas import TaskStatus, TaskGraph

logger = logging.getLogger("orchestrator")


class OrchestratorStateMachine:
    """
    Deterministic state machine for executing task graph nodes.
    """
    def __init__(self, graph: TaskGraph):
        self.graph = graph

    def update_node_statuses(self) -> List[str]:
        """
        Evaluates nodes and transitions eligible ones to READY.
        Handles both initial PENDING nodes and nodes marked for RETRYING.
        """
        newly_ready = []
        for node_id, node in self.graph.nodes.items():
            # 1. Immediately reset RETRYING tasks to READY so they re-enter the queue
            if node.status == TaskStatus.RETRYING:
                node.status = TaskStatus.READY
                newly_ready.append(node_id)
                logger.info(f"Node {node_id} ({node.description[:30]}) is RETRYING -> set to READY.")
                continue

            # 2. Only evaluate PENDING nodes for dependency resolution
            if node.status != TaskStatus.PENDING:
                continue

            deps_passed = all(
                self.graph.nodes[dep_id].status == TaskStatus.PASSED
                for dep_id in node.dependencies
                if dep_id in self.graph.nodes
            )

            if deps_passed:
                node.status = TaskStatus.READY
                newly_ready.append(node_id)
                logger.info(f"Node {node_id} ({node.description[:30]}) dependencies met -> set to READY.")
                
        return newly_ready

    def handle_node_failure(self, node_id: str, reason: str) -> TaskStatus:
        """
        Increments retry counts, logs failure context, and determines 
        whether to retry or escalate to REPLANNING / FAILED.
        """
        node = self.graph.nodes[node_id]
        node.attempts += 1
        
        try:
            loop = asyncio.get_running_loop()
            timestamp = str(loop.time())
        except RuntimeError:
            timestamp = "0.0"

        node.failure_history.append({
            "attempt": node.attempts,
            "reason": reason,
            "timestamp": timestamp
        })

        if node.attempts < node.max_attempts:
            node.status = TaskStatus.RETRYING
            logger.warning(
                f"Node {node_id} failed. Retrying (Attempt {node.attempts}/{node.max_attempts}). Reason: {reason}"
            )
        else:
            # Mark node as FAILED if max retries are exhausted to avoid deadlocks
            node.status = TaskStatus.FAILED
            logger.error(f"Node {node_id} exhausted max attempts ({node.max_attempts}). Marking FAILED.")
            self.apply_cascading_invalidation(node_id)

        return node.status

    def apply_cascading_invalidation(self, failed_node_id: str) -> Set[str]:
        """
        Cascades failure downstream to all dependent nodes when a parent node permanently fails.
        """
        blocked_nodes: Set[str] = set()

        def mark_downstream(current_id: str):
            for child_id, child_node in self.graph.nodes.items():
                if current_id in child_node.dependencies:
                    if child_node.status in (TaskStatus.PASSED, TaskStatus.READY, TaskStatus.RUNNING, TaskStatus.PENDING):
                        child_node.status = TaskStatus.FAILED
                        blocked_nodes.add(child_id)
                        logger.warning(
                            f"Cascading Invalidation: Node {child_id} marked FAILED due to upstream failure in {current_id}"
                        )
                    mark_downstream(child_id)

        mark_downstream(failed_node_id)
        return blocked_nodes

    def is_terminal(self) -> bool:
        """
        Checks if the entire graph has reached a terminal state (no active, running, or ready tasks).
        """
        terminal_statuses = {TaskStatus.PASSED, TaskStatus.FAILED}
        return all(node.status in terminal_statuses for node in self.graph.nodes.values())


class Orchestrator:
    """
    In-memory project store and manager for TaskGraphs.
    """
    def __init__(self):
        self.projects: Dict[str, TaskGraph] = {}

    def register_graph(self, project_id: str, graph: TaskGraph):
        self.projects[project_id] = graph

    def get_graph(self, project_id: str) -> Optional[TaskGraph]:
        return self.projects.get(project_id)


# Global singleton instance exported for main.py and router modules
orchestrator = Orchestrator()