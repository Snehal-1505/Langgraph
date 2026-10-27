import React from 'react';
import {
  CheckCircle2,
  Clock,
  AlertCircle,
  Loader2,
  RefreshCw,
  XCircle,
  FileText,
  Search,
  Bot,
  Scale,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import { WorkflowEvent, ResearchStatus } from '../types';

interface StageDefinition {
  id: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const STAGES: StageDefinition[] = [
  { id: 'validation', label: 'Request Validation', description: 'Input sanity, constraints & safety verification', icon: ShieldCheck },
  { id: 'planning', label: 'Planner Agent', description: 'Deconstructing topic into 3-perspective tasks', icon: Bot },
  { id: 'researcher_trends', label: 'Researcher [Trends]', description: 'Web search for recent facts & adoption benchmarks', icon: Search },
  { id: 'researcher_benefits', label: 'Researcher [Benefits]', description: 'Empirical studies on productivity & advantages', icon: Search },
  { id: 'researcher_risks', label: 'Researcher [Risks]', description: 'Investigating failure modes, security & limits', icon: Search },
  { id: 'evidence_validation', label: 'Evidence Validation', description: 'SSRF verification, deduplication & passage grounding', icon: Scale },
  { id: 'analysis', label: 'Analyst Agent', description: 'Cross-perspective synthesis & conflict detection', icon: Sparkles },
  { id: 'writing', label: 'Writer Agent', description: 'Drafting 14-section comprehensive report', icon: FileText },
  { id: 'review', label: 'Reviewer Agent', description: 'Verifying citation integrity & section coverage', icon: CheckCircle2 },
  { id: 'finalization', label: 'Persistence & Checkpointing', description: 'Final report & source records saved to database', icon: CheckCircle2 },
];

interface ProgressTrackerProps {
  currentStage: string;
  status: ResearchStatus;
  events: WorkflowEvent[];
  onCancel?: () => void;
  onViewReport?: () => void;
  hasReport?: boolean;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  currentStage,
  status,
  events,
  onCancel,
  onViewReport,
  hasReport
}) => {
  // Determine status of each stage
  const getStageStatus = (stageId: string): 'pending' | 'running' | 'completed' | 'failed' => {
    if (status === 'failed' && currentStage.includes(stageId)) return 'failed';

    const stageOrder = STAGES.map(s => s.id);
    const currentIndex = stageOrder.indexOf(currentStage);
    const thisIndex = stageOrder.indexOf(stageId);

    // If session is completed, all stages are completed
    if (status === 'completed') return 'completed';

    // Direct check based on completed events
    const hasCompletedEvent = events.some(e => e.stage === stageId && (e.event_type === 'completed' || e.event_type === 'info'));
    if (hasCompletedEvent) return 'completed';

    if (currentStage === stageId || (stageId.startsWith('researcher_') && currentStage === 'researching')) {
      return 'running';
    }

    if (thisIndex < currentIndex && currentIndex !== -1) {
      return 'completed';
    }

    return 'pending';
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Live Multi-Agent Execution</h3>
            <span className={`text-[11px] font-semibold uppercase px-2.5 py-0.5 rounded-full border ${
              status === 'running' ? 'bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800 animate-pulse' :
              status === 'completed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800' :
              status === 'failed' ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800' :
              'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 border-slate-200'
            }`}>
              {status}
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Real-time LangGraph state updates and verified source collection</p>
        </div>

        <div className="flex items-center space-x-2">
          {status === 'running' && onCancel && (
            <button
              onClick={onCancel}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 border border-red-200 dark:border-red-800 transition-colors"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Cancel Research</span>
            </button>
          )}

          {hasReport && onViewReport && (
            <button
              onClick={onViewReport}
              className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-brand-600 text-white hover:bg-brand-500 shadow-sm transition-colors"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>View Generated Report</span>
            </button>
          )}
        </div>
      </div>

      {/* Stage Flow Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {STAGES.map((stg) => {
          const stgStatus = getStageStatus(stg.id);
          const Icon = stg.icon;

          return (
            <div
              key={stg.id}
              className={`flex items-start space-x-3 p-3 rounded-xl border transition-all ${
                stgStatus === 'running'
                  ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-950/20 shadow-sm'
                  : stgStatus === 'completed'
                  ? 'border-emerald-200/60 dark:border-emerald-900/30 bg-emerald-50/20 dark:bg-emerald-950/10'
                  : stgStatus === 'failed'
                  ? 'border-red-200 dark:border-red-900/40 bg-red-50/30 dark:bg-red-950/10'
                  : 'border-slate-100 dark:border-slate-800/60 opacity-60'
              }`}
            >
              <div className="pt-0.5">
                {stgStatus === 'running' ? (
                  <Loader2 className="w-4 h-4 text-brand-600 animate-spin" />
                ) : stgStatus === 'completed' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                ) : stgStatus === 'failed' ? (
                  <AlertCircle className="w-4 h-4 text-red-500" />
                ) : (
                  <Clock className="w-4 h-4 text-slate-400" />
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className={`text-xs font-semibold truncate ${
                    stgStatus === 'running' ? 'text-brand-900 dark:text-brand-300' :
                    stgStatus === 'completed' ? 'text-slate-800 dark:text-slate-200' :
                    'text-slate-500 dark:text-slate-400'
                  }`}>
                    {stg.label}
                  </h4>
                  <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider ml-1">
                    {stgStatus}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate mt-0.5">
                  {stg.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Real-time Event Console Log */}
      <div className="space-y-2 pt-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
            Real-time Activity Log ({events.length} events)
          </span>
          {status === 'running' && (
            <span className="flex items-center space-x-1.5 text-[11px] text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              <span>Streaming events via SSE</span>
            </span>
          )}
        </div>

        <div className="h-44 overflow-y-auto rounded-xl bg-slate-900 text-slate-200 p-3.5 font-mono text-xs space-y-2 border border-slate-800">
          {events.length === 0 ? (
            <p className="text-slate-500 italic">Connecting to Server-Sent Events stream...</p>
          ) : (
            events.map((ev, idx) => (
              <div key={idx} className="flex items-start space-x-2 leading-relaxed">
                <span className="text-slate-500 text-[10px] shrink-0 pt-0.5">
                  {new Date(ev.timestamp).toLocaleTimeString()}
                </span>
                <span className={`text-[10px] uppercase font-bold shrink-0 px-1 py-0.2 rounded ${
                  ev.event_type === 'error' ? 'bg-red-950 text-red-400' :
                  ev.event_type === 'completed' ? 'bg-emerald-950 text-emerald-400' :
                  'bg-slate-800 text-sky-400'
                }`}>
                  [{ev.stage}]
                </span>
                <span className={`text-slate-300 break-words ${ev.event_type === 'error' ? 'text-red-300' : ''}`}>
                  {ev.message}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
