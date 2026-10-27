import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { WorkspacePage } from './pages/WorkspacePage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './services/api';
import { ProviderStatus } from './types';

export const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('researchlab_theme') === 'dark';
  });
  const [providers, setProviders] = useState<ProviderStatus | null>(null);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('researchlab_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('researchlab_theme', 'light');
    }
  }, [darkMode]);

  useEffect(() => {
    api.getProviders()
      .then(setProviders)
      .catch((e) => console.warn('Could not fetch providers on boot', e));
  }, []);

  const handleToggleDarkMode = () => {
    setDarkMode((prev) => !prev);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
        <Navbar
          providers={providers}
          darkMode={darkMode}
          onToggleDarkMode={handleToggleDarkMode}
        />

        <div className="flex-1 flex overflow-hidden">
          <Sidebar />

          <main className="flex-1 overflow-y-auto p-4 sm:p-8">
            <Routes>
              <Route path="/" element={<WorkspacePage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
