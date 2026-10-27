import React, { useState } from 'react';
import { Sparkles, ArrowRight, Compass, ShieldAlert, Zap, Layers, HelpCircle } from 'lucide-react';
import { ResearchDepth } from '../types';

interface ResearchFormProps {
  onSubmit: (params: {
    topic: string;
    scope?: string;
    depth: ResearchDepth;
    max_sources: number;
  }) => void;
  isLoading: boolean;
}

const EXAMPLE_TOPICS = [
  "Analyze the impact of generative AI on software development, including productivity, employment, risks, limitations, and future trends.",
  "Evaluate quantum computing progress in cryptography: RSA vulnerability timelines and post-quantum migration.",
  "Autonomous AI agents in healthcare diagnostics: accuracy benchmarks, clinical adoption barriers, and ethical liabilities."
];

export const ResearchForm: React.FC<ResearchFormProps> = ({ onSubmit, isLoading }) => {
  const [topic, setTopic] = useState('');
  const [scope, setScope] = useState('');
  const [depth, setDepth] = useState<ResearchDepth>('standard');
  const [maxSources, setMaxSources] = useState<number>(4);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanTopic = topic.trim();
    if (!cleanTopic || cleanTopic.length < 3) {
      setValidationError('Please enter a research topic of at least 3 characters.');
      return;
    }
    setValidationError(null);
    onSubmit({
      topic: cleanTopic,
      scope: scope.trim() || undefined,
      depth,
      max_sources: maxSources,
    });
  };

  const handleSelectExample = (ex: string) => {
    setTopic(ex);
    setValidationError(null);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 py-6">
      {/* Hero Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 text-xs font-semibold border border-brand-200 dark:border-brand-800">
          <Sparkles className="w-3.5 h-3.5 text-brand-500" />
          <span>Multi-Perspective Autonomous Investigation</span>
        </div>
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
          What would you like to investigate?
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400 max-w-xl mx-auto">
          Enter a topic and our 5 specialized LangGraph AI agents will collaborate: planning queries, gathering web evidence in parallel, detecting conflicts, drafting reports, and checking citations.
        </p>
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 space-y-6">
        {/* Research Topic Input */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label htmlFor="topic" className="block text-sm font-semibold text-slate-900 dark:text-slate-100">
              Primary Research Question or Topic <span className="text-red-500">*</span>
            </label>
            <span className={`text-xs ${topic.length > 450 ? 'text-amber-500 font-bold' : 'text-slate-400'}`}>
              {topic.length}/500
            </span>
          </div>
          <textarea
            id="topic"
            rows={3}
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            maxLength={500}
            placeholder="e.g., Analyze the impact of generative AI on software development, including productivity, employment, risks, limitations, and future trends."
            className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50 px-4 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:border-brand-500 focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500/20 transition-all text-sm resize-none"
          />
          {validationError && (
            <p className="text-xs text-red-500 font-medium flex items-center space-x-1">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>{validationError}</span>
            </p>
          )}

          {/* Quick Example Pills */}
          <div className="pt-1">
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400 mr-2">Try an example:</span>
            <div className="flex flex-wrap gap-1.5 mt-1.5">
              {EXAMPLE_TOPICS.map((ex, i) => (
                <button
                  type="button"
                  key={i}
                  onClick={() => handleSelectExample(ex)}
                  className="text-[11px] text-left px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-brand-50 hover:text-brand-700 dark:hover:bg-brand-950/40 dark:hover:text-brand-300 border border-slate-200 dark:border-slate-700 transition-colors"
                >
                  {ex.length > 55 ? ex.substring(0, 55) + '...' : ex}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Optional Scope Context */}
        <div className="space-y-2">
          <label htmlFor="scope" className="block text-sm font-semibold text-slate-900 dark:text-slate-100">
            Scope & Constraints <span className="text-xs text-slate-400 font-normal">(Optional)</span>
          </label>
          <input
            id="scope"
            type="text"
            value={scope}
            onChange={(e) => setScope(e.target.value)}
            placeholder="e.g., Focus on empirical benchmarks from 2024-2026, enterprise team studies, and security audits"
            className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50 px-4 py-2.5 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:border-brand-500 focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500/20 transition-all text-sm"
          />
        </div>

        {/* Research Depth Selection */}
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100">
            Investigation Depth
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              {
                id: 'quick' as ResearchDepth,
                title: 'Quick Brief',
                desc: 'Fast overview, ~2 sources/perspective',
                icon: Zap,
                sources: 2,
              },
              {
                id: 'standard' as ResearchDepth,
                title: 'Standard (Recommended)',
                desc: 'Balanced inquiry, ~4 sources/perspective',
                icon: Compass,
                sources: 4,
              },
              {
                id: 'detailed' as ResearchDepth,
                title: 'Comprehensive',
                desc: 'Deep multi-source synthesis, ~6 sources',
                icon: Layers,
                sources: 6,
              },
            ].map((option) => {
              const Icon = option.icon;
              const isSelected = depth === option.id;
              return (
                <button
                  type="button"
                  key={option.id}
                  onClick={() => {
                    setDepth(option.id);
                    setMaxSources(option.sources);
                  }}
                  className={`text-left p-3.5 rounded-xl border transition-all ${
                    isSelected
                      ? 'border-brand-500 bg-brand-50/60 dark:bg-brand-950/30 ring-2 ring-brand-500/20'
                      : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <Icon className={`w-4 h-4 ${isSelected ? 'text-brand-600 dark:text-brand-400' : 'text-slate-400'}`} />
                    <span className={`text-sm font-semibold ${isSelected ? 'text-brand-950 dark:text-brand-200' : 'text-slate-800 dark:text-slate-200'}`}>
                      {option.title}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{option.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Max Sources Slider */}
        <div className="space-y-2 pt-2">
          <div className="flex items-center justify-between">
            <label htmlFor="maxSources" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Maximum Sources per Perspective
            </label>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700">
              {maxSources} sources
            </span>
          </div>
          <input
            id="maxSources"
            type="range"
            min={2}
            max={8}
            step={1}
            value={maxSources}
            onChange={(e) => setMaxSources(Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-brand-500"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !topic.trim()}
          className="w-full flex items-center justify-center space-x-2 py-3.5 px-6 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:bg-slate-300 dark:disabled:bg-slate-800 text-white font-semibold shadow-md shadow-brand-500/20 hover:shadow-brand-500/30 transition-all cursor-pointer disabled:cursor-not-allowed text-sm"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Initializing Multi-Agent Workflow...</span>
            </>
          ) : (
            <>
              <span>Start Autonomous Research</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
