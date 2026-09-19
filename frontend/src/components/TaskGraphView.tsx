import React from "react";
import { TaskGraph, TaskNode } from "../types";
import { StatusBadge } from "./StatusBadge";

interface TaskGraphViewProps {
  graph: TaskGraph | null;
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string) => void;
}

export const TaskGraphView: React.FC<TaskGraphViewProps> = ({
  graph,
  selectedNodeId,
  onSelectNode,
}) => {
  if (!graph || !graph.nodes || Object.keys(graph.nodes).length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 border border-slate-800 rounded-lg">
        No Task DAG Active. Submit a product specification to generate tasks.
      </div>
    );
  }

  const nodes = Object.values(graph.nodes);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 bg-slate-900/50 rounded-lg border border-slate-800">
      {nodes.map((node: TaskNode) => {
        const isSelected = selectedNodeId === node.task_id;
        return (
          <div
            key={node.task_id}
            onClick={() => onSelectNode(node.task_id)}
            className={`p-4 rounded-lg cursor-pointer transition-all border ${
              isSelected
                ? "border-blue-500 bg-blue-950/30 shadow-lg shadow-blue-500/10"
                : "border-slate-800 bg-slate-900 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-sm font-bold text-blue-400">
                {node.task_id}
              </span>
              <StatusBadge status={node.status} />
            </div>
            <p className="text-xs text-slate-300 line-clamp-2 mb-3">
              {node.description}
            </p>
            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800">
              <span className="capitalize">Agent: {node.assigned_agent}</span>
              <span>
                Attempts: {node.attempts ?? 0}/{node.max_attempts ?? 3}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};