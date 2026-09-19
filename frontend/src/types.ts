export enum AgentRole {
  PLANNER = "planner",
  CODER = "coder",
  TESTER = "tester",
  REVIEWER = "reviewer",
}

export enum TaskStatus {
  PENDING = "pending",
  READY = "ready",
  RUNNING = "running",
  IN_PROGRESS = "in_progress",
  PASSED = "passed",
  RETRYING = "retrying",
  COMPLETED = "completed",
  FAILED = "failed",
}

export interface Artifacts {
  files?: Record<string, string>;
  files_touched?: string[];
  diff?: string;
  test_results?: string;
  test_output?: string;
  review_notes?: string;
}

export interface TaskNode {
  task_id: string;
  description: string;
  assigned_agent: AgentRole;
  dependencies?: string[];
  status: TaskStatus;
  attempts?: number;
  max_attempts?: number;
  failure_history?: Array<Record<string, any>>;
  artifacts?: Artifacts;
}

export interface TaskGraph {
  project_id: string;
  nodes: Record<string, TaskNode>;
}