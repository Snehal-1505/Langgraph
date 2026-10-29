import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ResearchForm } from '../components/ResearchForm';
import { ProgressTracker } from '../components/ProgressTracker';
import { ReportViewer } from '../components/ReportViewer';
import { SourcesPanel } from '../components/SourcesPanel';
import { api } from '../services/api';
import {
  ResearchSession,
  WorkflowEvent,
  ReportRecord,
  SourceRecord,
  ResearchDepth
} from '../types';
import { FileText, Activity, BookOpen, RotateCcw, AlertTriangle } from 'lucide-react';

export const WorkspacePage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const querySessionId = searchParams.get('session');

  const [session, setSession] = useState<ResearchSession | null>(null);
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [report, setReport] = useState<ReportRecord | null>(null);
  const [sources, setSources] = useState<SourceRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'report' | 'progress' | 'sources'>('progress');
  const [errorNotice, setErrorNotice] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Load existing session if passed via query params
  useEffect(() => {
    if (querySessionId) {
      loadExistingSession(querySessionId);
    }
  }, [querySessionId]);

  const loadExistingSession = async (id: string) => {
    setIsLoading(true);
    setErrorNotice(null);
    try {
      const sess = await api.getSession(id);
      setSession(sess);

      if (sess.status === 'completed') {
        try {
          const rep = await api.getReport(id);
          setReport(rep);
          setActiveTab('report');
        } catch (e) {
          console.warn('Report not available yet', e);
        }
        try {
          const srcs = await api.getSources(id);
          setSources(srcs);
        } catch (e) {
          console.warn('Sources not available yet', e);
        }
      } else if (sess.status === 'running' || sess.status === 'pending') {
        setActiveTab('progress');
        connectSSE(id);
        startPolling(id);
      }
    } catch (err: any) {
      setErrorNotice(err.message || 'Failed to load session');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartResearch = async (params: {
    topic: string;
    scope?: string;
    depth: ResearchDepth;
    max_sources: number;
  }) => {
    setIsLoading(true);
    setErrorNotice(null);
    setEvents([]);
    setReport(null);
    setSources([]);

    try {
      const newSession = await api.createResearch(params);
      setSession(newSession);
      setSearchParams({ session: newSession.id });
      setActiveTab('progress');
      connectSSE(newSession.id);
      startPolling(newSession.id);
    } catch (err: any) {
      setErrorNotice(err.message || 'Failed to initiate research session');
    } finally {
      setIsLoading(false);
    }
  };

  // Helper: fetch report + sources when a session is completed
  const fetchCompletedData = useCallback(async (sessionId: string) => {
    try {
      const rep = await api.getReport(sessionId);
      setReport(rep);
      setActiveTab('report');
    } catch (err) {
      console.warn('Could not fetch report', err);
    }
    try {
      const srcs = await api.getSources(sessionId);
      setSources(srcs);
    } catch (err) {
      console.warn('Could not fetch sources', err);
    }
  }, []);

  // Polling fallback: check session status every 2 seconds
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const startPolling = useCallback((sessionId: string) => {
    stopPolling();
    pollingRef.current = setInterval(async () => {
      try {
        const sess = await api.getSession(sessionId);
        if (sess.status === 'completed') {
          stopPolling();
          setSession(sess);
          await fetchCompletedData(sessionId);
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
          }
        } else if (sess.status === 'failed' || sess.status === 'cancelled') {
          stopPolling();
          setSession(sess);
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
          }
        } else {
          // Update current_stage for progress display
          setSession(prev => prev ? { ...prev, current_stage: sess.current_stage, status: sess.status } : prev);
        }
      } catch (err) {
        console.warn('Polling error:', err);
      }
    }, 2000);
  }, [stopPolling, fetchCompletedData]);

  const connectSSE = (sessionId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const sse = new EventSource(api.getEventsUrl(sessionId));
    eventSourceRef.current = sse;

    sse.addEventListener('workflow_event', (e: MessageEvent) => {
      try {
        const evData: WorkflowEvent = JSON.parse(e.data);
        setEvents((prev) => [...prev, evData]);

        // Update active stage
        setSession((prev) => {
          if (!prev) return prev;
          const isDone = evData.event_type === 'completed' && evData.stage === 'completed';
          const isFailed = evData.event_type === 'error' || evData.stage === 'failed';
          return {
            ...prev,
            current_stage: evData.stage,
            status: isDone ? 'completed' : isFailed ? 'failed' : prev.status,
          };
        });

        // If completed or failed, fetch final report and sources
        if (evData.event_type === 'completed' || evData.stage === 'completed') {
          stopPolling();
          setTimeout(async () => {
            try {
              const rep = await api.getReport(sessionId);
              setReport(rep);
              setActiveTab('report');
            } catch (err) {
              console.warn('Could not fetch report immediately', err);
            }
            try {
              const srcs = await api.getSources(sessionId);
              setSources(srcs);
            } catch (err) {
              console.warn('Could not fetch sources immediately', err);
            }
          }, 800);
        }
      } catch (err) {
        console.error('Error parsing SSE event', err);
      }
    });

    sse.onerror = (err) => {
      console.warn('SSE stream notice:', err);
    };
  };

  const handleCancelResearch = async () => {
    if (!session) return;
    try {
      await api.cancelResearch(session.id);
      setSession((prev) => (prev ? { ...prev, status: 'cancelled' } : null));
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    } catch (err: any) {
      setErrorNotice(err.message || 'Failed to cancel research');
    }
  };

  const handleReset = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    stopPolling();
    setSession(null);
    setEvents([]);
    setReport(null);
    setSources([]);
    setErrorNotice(null);
    setSearchParams({});
    setActiveTab('progress');
  };

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      stopPolling();
    };
  }, [stopPolling]);

  return (
    <div className="space-y-6">
      {/* Error Banner */}
      {errorNotice && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300 text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{errorNotice}</span>
          </div>
          <button
            onClick={() => setErrorNotice(null)}
            className="text-xs font-semibold underline hover:no-underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* When no session exists, show the main input form */}
      {!session ? (
        <ResearchForm onSubmit={handleStartResearch} isLoading={isLoading} />
      ) : (
        <div className="space-y-6">
          {/* Active Session Overview Card */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="space-y-1 max-w-2xl">
              <span className="text-[11px] font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400">
                Active Investigation
              </span>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white leading-tight">
                {session.topic}
              </h2>
              {session.scope && (
                <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1">
                  Scope: {session.scope}
                </p>
              )}
            </div>

            <div className="flex items-center space-x-2 shrink-0">
              <button
                onClick={handleReset}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 transition-colors border border-slate-200 dark:border-slate-700"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>New Research</span>
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center space-x-2 border-b border-slate-200 dark:border-slate-800 pb-2">
            <button
              onClick={() => setActiveTab('progress')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'progress'
                  ? 'bg-brand-500 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Workflow Progress ({events.length})</span>
            </button>

            {report && (
              <button
                onClick={() => setActiveTab('report')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'report'
                    ? 'bg-brand-500 text-white shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Final Report</span>
              </button>
            )}

            {sources.length > 0 && (
              <button
                onClick={() => setActiveTab('sources')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'sources'
                    ? 'bg-brand-500 text-white shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Sources & Evidence ({sources.length})</span>
              </button>
            )}
          </div>

          {/* Tab Content Panels */}
          {activeTab === 'progress' && (
            <ProgressTracker
              currentStage={session.current_stage}
              status={session.status}
              events={events}
              onCancel={handleCancelResearch}
              onViewReport={report ? () => setActiveTab('report') : undefined}
              hasReport={!!report}
            />
          )}

          {activeTab === 'report' && report && (
            <ReportViewer report={report} sources={sources} />
          )}

          {activeTab === 'sources' && (
            <SourcesPanel sources={sources} />
          )}
        </div>
      )}
    </div>
  );
};
