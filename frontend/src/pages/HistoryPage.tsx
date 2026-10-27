import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  History,
  Search,
  ExternalLink,
  Trash2,
  Calendar,
  AlertCircle,
  CheckCircle2,
  Clock,
  XCircle,
  FileText
} from 'lucide-react';
import { api } from '../services/api';
import { ResearchSession } from '../types';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setIsLoading(true);
    try {
      const data = await api.listSessions(0, 50);
      setSessions(data);
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      setSessionToDelete(null);
    } catch (err) {
      console.error('Failed to delete session', err);
    }
  };

  const filteredSessions = sessions.filter((s) =>
    s.topic.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-4">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center space-x-2">
            <History className="w-6 h-6 text-brand-500" />
            <span>Research History</span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Persisted sessions, evidence records, and finalized reports
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Filter past topics..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
          />
        </div>
      </div>

      {/* Sessions List */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400">
          <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-xs">Loading research archives...</p>
        </div>
      ) : filteredSessions.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
          <FileText className="w-10 h-10 text-slate-300 dark:text-slate-600 mx-auto" />
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
            {searchTerm ? 'No sessions match your search filter.' : 'No research sessions conducted yet.'}
          </p>
          <button
            onClick={() => navigate('/')}
            className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline"
          >
            Start your first investigation &rarr;
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {filteredSessions.map((sess) => (
            <div
              key={sess.id}
              className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm"
            >
              <div className="space-y-1.5 flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
                    sess.status === 'completed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800' :
                    sess.status === 'running' ? 'bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800' :
                    sess.status === 'failed' ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800' :
                    'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700'
                  }`}>
                    {sess.status === 'completed' && <CheckCircle2 className="w-3 h-3 text-emerald-500" />}
                    {sess.status === 'running' && <Clock className="w-3 h-3 text-sky-500 animate-spin" />}
                    {sess.status === 'failed' && <AlertCircle className="w-3 h-3 text-red-500" />}
                    {sess.status === 'cancelled' && <XCircle className="w-3 h-3 text-slate-400" />}
                    <span className="uppercase">{sess.status}</span>
                  </span>

                  <span className="text-xs text-slate-400 capitalize">{sess.depth} depth</span>
                </div>

                <h3 className="text-sm font-bold text-slate-900 dark:text-white truncate">
                  {sess.topic}
                </h3>

                <div className="flex items-center space-x-4 text-xs text-slate-500 dark:text-slate-400">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3 text-slate-400" />
                    <span>{new Date(sess.created_at).toLocaleString()}</span>
                  </span>
                  <span>&bull;</span>
                  <span className="font-mono text-[11px]">{sess.id.substring(0, 8)}...</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 shrink-0">
                <button
                  onClick={() => navigate(`/?session=${sess.id}`)}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-brand-50 hover:bg-brand-100 dark:bg-brand-950/40 dark:hover:bg-brand-950/70 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-800 transition-colors"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open Report</span>
                </button>

                <button
                  onClick={() => setSessionToDelete(sess.id)}
                  className="p-2 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                  title="Delete Session"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {sessionToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 max-w-sm w-full p-6 space-y-4 shadow-xl">
            <h4 className="text-base font-bold text-slate-900 dark:text-white">Delete Research Session?</h4>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              This will permanently remove the research report, all collected source records, and workflow checkpoints from the database.
            </p>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setSessionToDelete(null)}
                className="px-3.5 py-1.5 text-xs font-medium rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(sessionToDelete)}
                className="px-3.5 py-1.5 text-xs font-medium rounded-xl bg-red-600 hover:bg-red-500 text-white shadow-sm"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
