import React, { useState, useEffect } from 'react';
import { Database, Plus, Download, Tag, CheckSquare, XSquare } from 'lucide-react';
import { Dataset } from '../types';
import { api } from '../api/client';

export const Datasets: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  
  useEffect(() => {
    api.datasets.list().then(setDatasets);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Datasets & Annotation</h1>
          <p className="text-slate-400">Manage training data and perform manual labeling</p>
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 bg-accent-purple/20 text-accent-purple border border-accent-purple/50 rounded-xl hover:bg-accent-purple hover:text-white transition-all">
          <Plus className="w-4 h-4" />
          <span>New Dataset</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-card p-6">
          <div className="text-sm text-slate-400 mb-1">Total Conversations</div>
          <div className="text-3xl font-bold">12,450</div>
        </div>
        <div className="glass-card p-6">
          <div className="text-sm text-slate-400 mb-1">Annotated</div>
          <div className="text-3xl font-bold text-accent-cyan">8,230</div>
        </div>
        <div className="glass-card p-6">
          <div className="text-sm text-slate-400 mb-1">Cohen's Kappa (Agreement)</div>
          <div className="text-3xl font-bold text-risk-safe">0.82 <span className="text-sm font-normal text-slate-500">Substantial</span></div>
        </div>
      </div>

      <div className="glass-card p-0 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-dark-900/50">
            <tr>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Name</th>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Description</th>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Size</th>
              <th className="px-6 py-4 text-sm font-medium text-slate-400">Created</th>
              <th className="px-6 py-4 text-sm font-medium text-slate-400 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {datasets.map((ds) => (
              <tr key={ds.id} className="hover:bg-dark-800/30 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <Database className="w-4 h-4 text-accent-purple" />
                    <span className="font-medium text-slate-200">{ds.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-slate-400">{ds.description}</td>
                <td className="px-6 py-4 text-sm">{ds.conversation_count}</td>
                <td className="px-6 py-4 text-sm text-slate-500">{new Date(ds.created_at).toLocaleDateString()}</td>
                <td className="px-6 py-4 text-right">
                  <div className="flex justify-end space-x-2">
                    <button className="p-2 hover:bg-dark-700 rounded-lg text-slate-400 hover:text-accent-blue transition-colors tooltip-trigger" title="Annotate">
                      <Tag className="w-4 h-4" />
                    </button>
                    <button className="p-2 hover:bg-dark-700 rounded-lg text-slate-400 hover:text-accent-cyan transition-colors tooltip-trigger" title="Export">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
