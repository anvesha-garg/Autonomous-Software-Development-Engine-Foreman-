import React from "react";
import { TaskNode } from "../types";

interface DiffViewerProps {
  node: TaskNode | null;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ node }) => {
  if (!node) {
    return (
      <div className="flex items-center justify-center h-full p-6 text-center text-slate-500 border border-slate-800 rounded-lg">
        Select a task node from the graph to inspect generated code diffs and test results.
      </div>
    );
  }

  const { artifacts, failure_history } = node;

  return (
    <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-4 text-slate-200 h-full overflow-y-auto">
      <div>
        <h3 className="text-lg font-bold text-white mb-1">{node.task_id}</h3>
        <p className="text-xs text-slate-400">{node.description}</p>
      </div>

      {/* Code Diffs */}
      {artifacts?.diff && (
        <div className="space-y-1">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Generated Code / Diffs
          </h4>
          <pre className="p-3 text-xs font-mono bg-slate-950 text-emerald-400 rounded-md overflow-x-auto border border-slate-800">
            {artifacts.diff}
          </pre>
        </div>
      )}

      {/* Test Output */}
      {(artifacts?.test_output || artifacts?.test_results) && (
        <div className="space-y-1">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Test Execution Results
          </h4>
          <pre className="p-3 text-xs font-mono bg-slate-950 text-blue-300 rounded-md overflow-x-auto border border-slate-800">
            {artifacts.test_output || artifacts.test_results}
          </pre>
        </div>
      )}

      {/* Review Notes */}
      {artifacts?.review_notes && (
        <div className="space-y-1">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Reviewer Agent Notes
          </h4>
          <p className="p-3 text-xs bg-slate-950 text-slate-300 rounded-md border border-slate-800">
            {artifacts.review_notes}
          </p>
        </div>
      )}

      {/* Failure History */}
      {Array.isArray(failure_history) && failure_history.length > 0 && (
        <div className="space-y-1">
          <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider">
            Failure History ({failure_history.length})
          </h4>
          <div className="space-y-2">
            {failure_history.map((fail, index) => (
              <pre
                key={index}
                className="p-2 text-xs font-mono bg-rose-950/30 text-rose-300 rounded border border-rose-900/50 overflow-x-auto"
              >
                {typeof fail === "object"
                  ? JSON.stringify(fail, null, 2)
                  : String(fail)}
              </pre>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};