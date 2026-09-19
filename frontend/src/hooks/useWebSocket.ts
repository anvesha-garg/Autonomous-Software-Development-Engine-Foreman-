import { useState, useRef, useCallback } from "react";
import { TaskGraph } from "../types";

export const useWebSocket = (onGraphUpdate: (graph: TaskGraph) => void) => {
  const [logs, setLogs] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const startStream = useCallback((projectId: string) => {
    if (!projectId) return;

    // Close existing socket if connected
    if (wsRef.current) {
      wsRef.current.close();
    }

    setLogs((prev) => [...prev, `[SYSTEM]: Connecting stream for project ${projectId}...`]);

    const wsUrl = `ws://localhost:8000/projects/${projectId}/stream`;
    const socket = new WebSocket(wsUrl);
    wsRef.current = socket;

    socket.onopen = () => {
      setLogs((prev) => [...prev, `[SYSTEM]: Stream connected.`]);
    };

    socket.onmessage = (event) => {
      try {
        const updatedGraph: TaskGraph = JSON.parse(event.data);
        onGraphUpdate(updatedGraph);

        // Auto-generate UI log entries for node status updates
        if (updatedGraph.nodes) {
          Object.values(updatedGraph.nodes).forEach((node: any) => {
            if (node.status === "RUNNING") {
              setLogs((prev) => [
                ...prev,
                `[AGENT - ${node.assigned_agent.toUpperCase()}]: Task ${node.task_id} is running...`,
              ]);
            } else if (node.status === "PASSED") {
              setLogs((prev) => [
                ...prev,
                `[AGENT - ${node.assigned_agent.toUpperCase()}]: Task ${node.task_id} completed successfully.`,
              ]);
            }
          });
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    socket.onerror = (err) => {
      console.error("WebSocket Error:", err);
      setLogs((prev) => [...prev, `[ERROR]: Stream connection error.`]);
    };

    socket.onclose = () => {
      setLogs((prev) => [...prev, `[SYSTEM]: Stream disconnected.`]);
    };
  }, [onGraphUpdate]);

  return { logs, startStream };
};