import React from 'react';
import { TaskStatus } from '../types';

interface Props {
  status: TaskStatus;
}

const statusStyles: Record<TaskStatus, string> = {
  pending: 'bg-slate-800 text-slate-400 border-slate-700',
  ready: 'bg-blue-950 text-blue-400 border-blue-800',
  running: 'bg-amber-950 text-amber-400 border-amber-800 animate-pulse',
  passed: 'bg-emerald-950 text-emerald-400 border-emerald-800',
  failed: 'bg-rose-950 text-rose-400 border-rose-800',
  retrying: 'bg-orange-950 text-orange-400 border-orange-800',
  replanning: 'bg-purple-950 text-purple-400 border-purple-800',
  blocked: 'bg-red-950 text-red-500 border-red-900 border-dashed',
};

export const StatusBadge: React.FC<Props> = ({ status }) => {
  return (
    <span
      className={`px-2 py-0.5 text-xs font-mono rounded border uppercase tracking-wider ${
        statusStyles[status] || 'bg-slate-800 text-slate-400'
      }`}
    >
      {status}
    </span>
  );
};