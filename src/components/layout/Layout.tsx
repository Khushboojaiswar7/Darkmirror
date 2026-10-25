import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { motion, AnimatePresence } from 'framer-motion';

export const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-dark-950 text-slate-200 flex">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 p-8 overflow-y-auto relative">
          <div className="absolute inset-0 bg-gradient-radial from-accent-purple/5 to-transparent opacity-50 pointer-events-none" />
          <div className="max-w-7xl mx-auto relative z-0">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
