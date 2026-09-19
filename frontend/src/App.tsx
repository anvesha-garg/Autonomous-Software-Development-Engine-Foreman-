import React, { useState, useCallback } from "react";
import { TaskGraphView } from "./components/TaskGraphView";
import { WorkspaceViewer } from "./components/WorkspaceViewer";
import { LogStream } from "./components/LogStream";
import { useWebSocket } from "./hooks/useWebSocket";
import { TaskGraph } from "./types";

export const App: React.FC = () => {
  const [prompt, setPrompt] = useState("");
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [graph, setGraph] = useState<TaskGraph | null>(null);

  // Wrap state updater in useCallback to maintain a stable reference
  const handleGraphUpdate = useCallback((updatedGraph: TaskGraph) => {
    setGraph(updatedGraph);
  }, []);

  const { logs, startStream } = useWebSocket(handleGraphUpdate);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    try {
      const response = await fetch("http://localhost:8000/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const data = await response.json();

      if (data.graph) {
        setGraph(data.graph);
      }

      if (data.project_id) {
        startStream(data.project_id);
      }
    } catch (err) {
      console.error("Failed to decompose task:", err);
    }
  };

  const selectedNode =
    graph && selectedNodeId && graph.nodes ? graph.nodes[selectedNodeId] || null : null;

  const aggregatedWorkspaceFiles: Record<string, string> = {};
  if (graph && graph.nodes) {
    Object.values(graph.nodes).forEach((node: any) => {
      if (node?.artifacts?.files && typeof node.artifacts.files === "object") {
        Object.assign(aggregatedWorkspaceFiles, node.artifacts.files);
      } else if (node?.code && typeof node.code === "string") {
        const fileName = node.task_id ? `${node.task_id}.py` : "generated_code.py";
        aggregatedWorkspaceFiles[fileName] = node.code;
      }
    });
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 flex flex-col space-y-6">
      <header className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight">
            AI Autonomous Software Development Engine
          </h1>
          <p className="text-xs text-slate-400">
            Deterministic State Machine Orchestration
          </p>
        </div>
        {graph?.project_id && (
          <span className="font-mono text-xs bg-slate-900 border border-slate-800 px-3 py-1 rounded-md text-slate-400">
            Project ID: {graph.project_id}
          </span>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        <div className="lg:col-span-2 space-y-6 flex flex-col">
          <form onSubmit={handleSubmit} className="bg-slate-900 p-4 rounded-lg border border-slate-800 space-y-3">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter product specification (e.g. Build auth.py and test_auth.py)..."
              className="w-full h-24 p-3 text-sm bg-slate-950 border border-slate-800 rounded-md focus:outline-none focus:border-blue-500 text-slate-200 resize-none"
            />
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-500 rounded-md transition-colors"
              >
                Decompose & Execute DAG
              </button>
            </div>
          </form>

          <TaskGraphView
            graph={graph}
            selectedNodeId={selectedNodeId}
            onSelectNode={(nodeId) => setSelectedNodeId(nodeId)}
          />

          <LogStream logs={logs} />
        </div>

        <div className="lg:col-span-1">
          <WorkspaceViewer
            projectId={graph?.project_id}
            workspaceFiles={aggregatedWorkspaceFiles}
            selectedTask={selectedNode}
          />
        </div>
      </div>
    </div>
  );
};

export default App;