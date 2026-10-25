import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileSearch, BrainCircuit, BarChart2, Microchip, FlaskConical, Database, FileText, LogOut } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Audit', path: '/audit', icon: FileSearch },
  { name: 'Explainer', path: '/explainer', icon: BrainCircuit },
  { name: 'Analytics', path: '/analytics', icon: BarChart2 },
  { name: 'Research Mode', path: '/research', icon: Microchip },
  { name: 'Evaluation', path: '/evaluation', icon: FlaskConical },
  { name: 'Datasets', path: '/datasets', icon: Database },
  { name: 'Reports', path: '/reports', icon: FileText },
];

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuthStore();

  return (
    <div className="w-64 h-screen glass-card rounded-none border-y-0 border-l-0 flex flex-col fixed left-0 top-0">
      <div className="p-6 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl gradient-border flex items-center justify-center bg-dark-900 shadow-[0_0_15px_rgba(139,92,246,0.5)]">
          <span className="text-xl font-bold gradient-text">DM</span>
        </div>
        <h1 className="text-xl font-bold tracking-wider text-slate-100">DARKMIRROR</h1>
      </div>

      <nav className="flex-1 px-4 space-y-2 mt-4 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                isActive
                  ? 'bg-accent-purple/20 text-accent-purple border border-accent-purple/30 shadow-[0_0_10px_rgba(139,92,246,0.2)]'
                  : 'text-slate-400 hover:bg-dark-800/50 hover:text-slate-200'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 mt-auto">
        <div className="p-4 glass-card-hover rounded-xl flex items-center justify-between">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-accent-purple to-accent-blue flex items-center justify-center shrink-0">
              <span className="text-sm font-bold">{user?.username ? user.username.charAt(0) : 'G'}</span>
            </div>
            <div className="truncate text-sm">
              <p className="font-semibold text-slate-200 truncate">{user?.username || 'Researcher'}</p>
              <p className="text-slate-500 text-xs truncate">{user?.email || 'researcher@darkmirror.ai'}</p>
            </div>
          </div>
          <button onClick={logout} className="text-slate-500 hover:text-risk-danger transition-colors p-1">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
