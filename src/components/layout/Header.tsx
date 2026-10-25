import React from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, Search } from 'lucide-react';

export const Header: React.FC = () => {
  const location = useLocation();
  const path = location.pathname;
  
  let pageTitle = 'Dashboard';
  if (path.includes('/audit')) pageTitle = 'Audit Workspace';
  else if (path.includes('/analytics')) pageTitle = 'Analytics';
  else if (path.includes('/research')) pageTitle = 'Research Mode';
  else if (path.includes('/evaluation')) pageTitle = 'Evaluation';
  else if (path.includes('/datasets')) pageTitle = 'Datasets';
  else if (path.includes('/reports')) pageTitle = 'Reports';

  return (
    <header className="h-20 glass-card rounded-none border-x-0 border-t-0 flex items-center justify-between px-8 sticky top-0 z-10 backdrop-blur-2xl bg-dark-950/60">
      <div>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-100 to-slate-400">
          {pageTitle}
        </h2>
      </div>

      <div className="flex items-center space-x-6">
        <div className="relative group hidden md:block">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-hover:text-accent-purple transition-colors" />
          <input
            type="text"
            placeholder="Search workspace..."
            className="bg-dark-900 border border-slate-700/50 rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-accent-purple/50 focus:ring-1 focus:ring-accent-purple/50 transition-all w-64 text-slate-200 placeholder-slate-500"
          />
        </div>
        
        <button className="relative p-2 rounded-full hover:bg-dark-800/50 text-slate-400 hover:text-slate-100 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-accent-purple rounded-full animate-pulse-slow"></span>
        </button>
      </div>
    </header>
  );
};
