import React from 'react';
import { NavLink } from 'react-router-dom';
import { PlusCircle, History, Settings, Bot, BookOpen, Layers } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'New Research', icon: PlusCircle },
    { to: '/history', label: 'Research History', icon: History },
    { to: '/settings', label: 'Model & Providers', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col justify-between p-4 shrink-0">
      <div className="space-y-6">
        {/* Navigation Section */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-brand-500 text-white shadow-sm shadow-brand-500/25 font-semibold'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* 5-Agent Architecture Guide Pill */}
        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-700 dark:text-slate-300">
            <Layers className="w-3.5 h-3.5 text-brand-500" />
            <span>Active Agents</span>
          </div>
          <ul className="text-[11px] text-slate-500 dark:text-slate-400 space-y-1">
            <li className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              <span>Planner Agent</span>
            </li>
            <li className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-sky-500" />
              <span>3x Parallel Researchers</span>
            </li>
            <li className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
              <span>Analyst Agent</span>
            </li>
            <li className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>Writer Agent (14 Secs)</span>
            </li>
            <li className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
              <span>Reviewer Agent (QC)</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-4 border-t border-slate-200 dark:border-slate-800 text-[11px] text-slate-400 dark:text-slate-500 flex items-center justify-between">
        <span>LangGraph Orchestrator</span>
        <span className="font-mono">v1.0.0</span>
      </div>
    </aside>
  );
};
