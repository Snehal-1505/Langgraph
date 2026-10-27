import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import {
  Download,
  FileText,
  CheckCircle,
  AlertTriangle,
  ExternalLink,
  BookOpen,
  Calendar,
  Share2,
  Copy,
  Check
} from 'lucide-react';
import { ReportRecord, SourceRecord } from '../types';
import { api } from '../services/api';

interface ReportViewerProps {
  report: ReportRecord;
  sources: SourceRecord[];
}

export const ReportViewer: React.FC<ReportViewerProps> = ({ report, sources }) => {
  const [copied, setCopied] = useState(false);

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(report.markdown_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <article className="space-y-8 max-w-4xl mx-auto">
      {/* Report Header Card */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100 dark:border-slate-800">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                report.review_status === 'passed'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                  : 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800'
              }`}>
                {report.review_status === 'passed' ? (
                  <>
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                    <span>QC Review: Approved</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                    <span>QC Review: Advisory Note</span>
                  </>
                )}
              </span>
              <span className="text-xs text-slate-400 font-mono">v{report.version}</span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              {report.title}
            </h1>

            <div className="flex items-center space-x-4 text-xs text-slate-500 dark:text-slate-400">
              <span className="flex items-center space-x-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>{new Date(report.created_at).toLocaleDateString(undefined, { dateStyle: 'medium' })}</span>
              </span>
              <span>&bull;</span>
              <span className="flex items-center space-x-1">
                <BookOpen className="w-3.5 h-3.5" />
                <span>{sources.length} Verified Sources</span>
              </span>
            </div>
          </div>

          {/* Export Actions */}
          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={handleCopyMarkdown}
              className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors border border-slate-200 dark:border-slate-700"
              title="Copy Raw Markdown"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>

            <a
              href={api.getMarkdownExportUrl(report.session_id)}
              download
              className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors border border-slate-200 dark:border-slate-700"
              title="Download Markdown"
            >
              <Download className="w-4 h-4" />
              <span>.MD</span>
            </a>

            <a
              href={api.getPdfExportUrl(report.session_id)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white shadow-sm shadow-brand-500/20 transition-all"
              title="Download Formatted PDF"
            >
              <FileText className="w-4 h-4" />
              <span>Export PDF</span>
            </a>
          </div>
        </div>

        {/* Executive Summary Callout */}
        {report.executive_summary && (
          <div className="p-4 sm:p-5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border-l-4 border-brand-500 dark:border-brand-400 space-y-1.5">
            <div className="text-xs font-bold uppercase tracking-wider text-brand-700 dark:text-brand-300">
              Executive Briefing
            </div>
            <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              {report.executive_summary}
            </p>
          </div>
        )}

        {/* Markdown Content Section */}
        <div className="prose prose-slate dark:prose-invert max-w-none pt-4 prose-headings:font-bold prose-headings:tracking-tight prose-a:text-brand-600 dark:prose-a:text-brand-400 prose-a:no-underline hover:prose-a:underline prose-li:my-1">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeSanitize]}
            components={{
              a: ({ node, ...props }) => (
                <a {...props} target="_blank" rel="noopener noreferrer" className="font-semibold inline-flex items-center space-x-0.5 text-brand-600 dark:text-brand-400">
                  <span>{props.children}</span>
                  <ExternalLink className="w-3 h-3 ml-0.5 inline opacity-70" />
                </a>
              ),
              h2: ({ node, ...props }) => (
                <h2 {...props} className="text-xl font-bold mt-8 mb-4 pb-2 border-b border-slate-100 dark:border-slate-800 text-slate-900 dark:text-slate-100" />
              ),
              h3: ({ node, ...props }) => (
                <h3 {...props} className="text-base font-semibold mt-6 mb-2 text-slate-800 dark:text-slate-200" />
              )
            }}
          >
            {report.markdown_content}
          </ReactMarkdown>
        </div>
      </div>
    </article>
  );
};
