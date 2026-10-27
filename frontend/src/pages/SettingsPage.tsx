import React, { useState, useEffect } from 'react';
import {
  Settings,
  Cpu,
  Search,
  ShieldCheck,
  Terminal,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { ProviderStatus } from '../types';

export const SettingsPage: React.FC = () => {
  const [providers, setProviders] = useState<ProviderStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    setIsLoading(true);
    try {
      const data = await api.getProviders();
      setProviders(data);
    } catch (err) {
      console.error('Failed to load provider status', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      {/* Page Title */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center space-x-2">
          <Settings className="w-6 h-6 text-brand-500" />
          <span>AI Models & Research Providers</span>
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Free-first architecture: Runs locally via Ollama with optional zero-cost cloud fallbacks
        </p>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-slate-400">
          <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-xs">Checking provider health...</p>
        </div>
      ) : providers && (
        <div className="grid grid-cols-1 gap-6">
          {/* Active LLM Provider Card */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center space-x-2.5">
                <div className="w-9 h-9 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center border border-brand-200 dark:border-brand-800">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">Active LLM Provider</h3>
                  <span className="text-xs font-mono text-slate-500">{providers.llm_provider.toUpperCase()}</span>
                </div>
              </div>

              <span className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                providers.ollama_status === 'ready' || providers.llm_provider === 'mock'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                  : 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800'
              }`}>
                {providers.ollama_status === 'ready' || providers.llm_provider === 'mock' ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Operational</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
                    <span>Ollama Unreachable (Mock Active)</span>
                  </>
                )}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 space-y-1">
                <span className="text-slate-500 dark:text-slate-400">Configured Model</span>
                <p className="font-mono font-semibold text-slate-900 dark:text-white">{providers.configured_model}</p>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 space-y-1">
                <span className="text-slate-500 dark:text-slate-400">Endpoint / URL</span>
                <p className="font-mono text-slate-900 dark:text-white truncate">{providers.ollama_base_url}</p>
              </div>
            </div>

            {/* Ollama Terminal Setup Guide */}
            <div className="p-4 rounded-xl bg-slate-950 text-slate-200 space-y-2 border border-slate-800">
              <div className="flex items-center space-x-2 text-xs font-bold text-sky-400">
                <Terminal className="w-4 h-4" />
                <span>Ollama Local Model Setup (Windows PowerShell)</span>
              </div>
              <p className="text-[11px] text-slate-400">
                To run completely private and free AI on your local machine, download Ollama from <a href="https://ollama.com" target="_blank" rel="noreferrer" className="underline text-sky-400">ollama.com</a> and run:
              </p>
              <div className="font-mono text-xs bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-emerald-400 select-all">
                ollama pull llama3.2<br />
                ollama serve
              </div>
            </div>
          </div>

          {/* Web Search Provider Card */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center space-x-2.5">
                <div className="w-9 h-9 rounded-xl bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-400 flex items-center justify-center border border-sky-200 dark:border-sky-800">
                  <Search className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">Web Search Provider</h3>
                  <span className="text-xs font-mono text-slate-500 capitalize">{providers.search_provider}</span>
                </div>
              </div>

              <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                <span>Ready ({providers.active_search_status})</span>
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 text-xs text-slate-600 dark:text-slate-300 space-y-1.5">
              <div className="flex items-center space-x-1 font-semibold text-slate-900 dark:text-white">
                <Info className="w-3.5 h-3.5 text-brand-500" />
                <span>Zero-Key Default Fallback</span>
              </div>
              <p>
                DuckDuckGo search runs automatically without requiring an API key. Tavily is supported as an optional provider when <code className="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded font-mono">TAVILY_API_KEY</code> is supplied in your <code className="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded font-mono">.env</code> file.
              </p>
            </div>
          </div>

          {/* Security & SSRF Protection Card */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-3 shadow-sm">
            <div className="flex items-center space-x-2.5">
              <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-200 dark:border-emerald-800">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Network & Content Security Policies</h3>
                <p className="text-xs text-slate-500">Autonomous safeguards enforced on every web query</p>
              </div>
            </div>

            <ul className="text-xs text-slate-600 dark:text-slate-300 space-y-1.5 pt-2 list-disc list-inside">
              <li><strong>SSRF Guard:</strong> Restricts all fetches to external public HTTP/HTTPS URLs. Blocks localhost, 127.0.0.1, RFC 1918 private ranges, and link-local interfaces.</li>
              <li><strong>Prompt Injection Sanitizer:</strong> Automatically filters system override phrases and malicious instructions from scraped HTML.</li>
              <li><strong>Size & Timeout Bounds:</strong> Pages exceeding size boundaries or 20s timeouts are safely terminated without halting the workflow.</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
