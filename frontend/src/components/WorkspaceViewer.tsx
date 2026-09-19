import React, { useState } from "react";
import { Download, Copy, Check, FileCode } from "lucide-react";

interface WorkspaceViewerProps {
  projectId?: string;
  workspaceFiles?: Record<string, string>;
  selectedTask?: any;
  graph?: any;
}

export const WorkspaceViewer: React.FC<WorkspaceViewerProps> = ({
  projectId,
  workspaceFiles = {},
  selectedTask,
  graph,
}) => {
  // Aggregate files dynamically from selectedTask, props, or graph nodes
  const aggregatedFiles: Record<string, string> = { ...workspaceFiles };

  if (selectedTask?.artifacts?.files) {
    Object.assign(aggregatedFiles, selectedTask.artifacts.files);
  }

  if (graph?.nodes) {
    const nodesList = Array.isArray(graph.nodes)
      ? graph.nodes
      : Object.values(graph.nodes);

    nodesList.forEach((node: any) => {
      if (node?.artifacts?.files) {
        Object.assign(aggregatedFiles, node.artifacts.files);
      }
    });
  }

  const fileNames = Object.keys(aggregatedFiles);
  const [activeFile, setActiveFile] = useState<string | null>(fileNames[0] || null);
  const [copied, setCopied] = useState(false);

  const currentFile = activeFile && aggregatedFiles[activeFile] ? activeFile : fileNames[0];

  const handleCopy = (code: string) => {
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadZip = () => {
    if (!projectId) return;
    window.location.href = `http://localhost:8000/projects/${projectId}/download`;
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl flex flex-col h-full overflow-hidden text-slate-100 min-h-[500px]">
      <div className="flex items-center justify-between px-4 py-3 bg-slate-950 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <FileCode className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-sm">
            {selectedTask?.task_id ? `Task: ${selectedTask.task_id}` : "Generated Workspace Code"}
          </h2>
        </div>

        <button
          onClick={handleDownloadZip}
          disabled={!projectId}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors shadow-sm"
        >
          <Download className="w-3.5 h-3.5" />
          Download .zip
        </button>
      </div>

      {fileNames.length > 0 ? (
        <>
          <div className="flex items-center gap-1 px-2 pt-2 bg-slate-950 border-b border-slate-800 overflow-x-auto">
            {fileNames.map((fileName) => (
              <button
                key={fileName}
                onClick={() => setActiveFile(fileName)}
                className={`px-3 py-1.5 text-xs font-mono rounded-t-md transition-colors ${
                  currentFile === fileName
                    ? "bg-slate-900 text-indigo-400 border-t-2 border-indigo-500 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/50"
                }`}
              >
                {fileName}
              </button>
            ))}
          </div>

          <div className="relative flex-1 p-4 bg-slate-900 overflow-auto font-mono text-xs leading-relaxed">
            {currentFile && aggregatedFiles[currentFile] && (
              <>
                <button
                  onClick={() => handleCopy(aggregatedFiles[currentFile])}
                  className="absolute top-3 right-3 p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-md transition-colors border border-slate-700"
                  title="Copy Code"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>

                <pre className="text-slate-200 whitespace-pre-wrap">
                  <code>{aggregatedFiles[currentFile]}</code>
                </pre>
              </>
            )}
          </div>
        </>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-sm gap-2 p-6 text-center">
          <p>No generated workspace files available yet.</p>
          <p className="text-xs text-slate-600">
            Submit a prompt to decompose and execute the DAG.
          </p>
        </div>
      )}
    </div>
  );
};