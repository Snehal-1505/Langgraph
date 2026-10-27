import React from 'react';
import { ExternalLink, Globe, Calendar, ShieldCheck, Quote } from 'lucide-react';
import { SourceRecord } from '../types';

interface SourcesPanelProps {
  sources: SourceRecord[];
}

export const SourcesPanel: React.FC<SourcesPanelProps> = ({ sources }) => {
  if (sources.length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500">
        No external web sources recorded for this research session.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
          <span>Collected Evidence & Sources</span>
          <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            {sources.length}
          </span>
        </h3>
        <span className="text-xs text-emerald-600 dark:text-emerald-400 flex items-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>All URLs validated against SSRF</span>
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {sources.map((src, idx) => (
          <div
            key={src.id || idx}
            className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all space-y-2.5 shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start space-x-2.5">
                <span className="w-6 h-6 rounded-lg bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 text-xs font-mono font-bold flex items-center justify-center shrink-0 border border-brand-200 dark:border-brand-800">
                  [{idx + 1}]
                </span>
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-white leading-snug">
                    {src.title || src.url}
                  </h4>
                  <div className="flex items-center space-x-3 text-xs text-slate-500 dark:text-slate-400 mt-1">
                    <span className="flex items-center space-x-1">
                      <Globe className="w-3 h-3 text-slate-400" />
                      <span>{src.domain}</span>
                    </span>
                    {src.publication_date && (
                      <span className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3 text-slate-400" />
                        <span>{src.publication_date}</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {src.url && !src.url.includes("offline.local") && (
                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-brand-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors shrink-0"
                  title="Open source URL in new tab"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>

            {src.extracted_evidence && (
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300 flex items-start space-x-2">
                <Quote className="w-3.5 h-3.5 text-brand-500 shrink-0 mt-0.5" />
                <p className="line-clamp-3 italic">
                  "{src.extracted_evidence}"
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
