import React, { useRef, useEffect } from 'react';
import { Terminal } from 'lucide-react';

interface Props {
  logs: any[];
}

export const LogStream: React.FC<Props> = ({ logs }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 h-full flex flex-col">
      <h3 className="text-xs uppercase font-semibold text-slate-400 mb-3 flex items-center gap-1.5">
        <Terminal className="w-3.5 h-3.5 text-indigo-400" /> Live Agent Execution Logs
      </h3>

      <div
        ref={scrollRef}
        className="bg-slate-950 p-3 rounded border border-slate-800 font-mono text-xs overflow-y-auto flex-1 space-y-2 max-h-56"
      >
        {logs.length === 0 ? (
          <span className="text-slate-600 font-mono">// System idle. Waiting for event stream...</span>
        ) : (
          logs.map((log, index) => {
            const timestamp = typeof log === 'object' && log?.timestamp ? log.timestamp : new Date().toLocaleTimeString();
            const agent = typeof log === 'object' ? log?.agent || log?.event_type : null;
            const message = typeof log === 'string' 
              ? log 
              : log?.message || log?.text || JSON.stringify(log);

            if (message === "[]" || !message) return null;

            return (
              <div key={log?.id || index} className="text-slate-300 leading-relaxed">
                <span className="text-slate-600 mr-2">[{timestamp}]</span>
                {agent && (
                  <span className="text-indigo-400 font-semibold mr-2">[{String(agent).toUpperCase()}]</span>
                )}
                <span>{message}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};