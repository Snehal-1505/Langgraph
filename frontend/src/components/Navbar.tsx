import React from 'react';
import { Cpu, Search, Sparkles, Moon, Sun, ShieldCheck } from 'lucide-react';
import { ProviderStatus } from '../types';

interface NavbarProps {
  providers?: ProviderStatus | null;
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ providers, darkMode, onToggleDarkMode }) => {
  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-30 px-6 flex items-center justify-between">
      {/* Brand */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-sky-400 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-bold text-lg text-slate-900 dark:text-white tracking-tight">ResearchLab AI</h1>
            <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
              Multi-Agent
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">Autonomous LangGraph Research Engine</p>
        </div>
      </div>

      {/* Status Badges & Controls */}
      <div className="flex items-center space-x-3">
        {providers && (
          <div className="hidden sm:flex items-center space-x-2">
            {/* LLM Status */}
            <div className="flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
              <Cpu className="w-3.5 h-3.5 text-brand-500" />
              <span>{providers.llm_provider.toUpperCase()}:</span>
              <span className="text-slate-900 dark:text-white font-semibold">{providers.configured_model}</span>
              <span className={`w-2 h-2 rounded-full ${providers.ollama_status === 'ready' || providers.llm_provider === 'mock' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
            </div>

            {/* Search Provider */}
            <div className="flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
              <Search className="w-3.5 h-3.5 text-sky-500" />
              <span>Search:</span>
              <span className="text-slate-900 dark:text-white font-semibold">{providers.search_provider}</span>
            </div>

            {/* SSRF Protection Badge */}
            <div className="hidden lg:flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>SSRF Guard</span>
            </div>
          </div>
        )}

        {/* Theme Toggle */}
        <button
          onClick={onToggleDarkMode}
          aria-label="Toggle dark mode"
          className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors border border-transparent hover:border-slate-200 dark:hover:border-slate-700"
        >
          {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>
      </div>
    </header>
  );
};
