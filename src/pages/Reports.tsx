import React from 'react';
import { FileText, Download, Filter, Search } from 'lucide-react';
import { mockDashboardStats } from '../api/mockData';

export const Reports: React.FC = () => {
  const reports = mockDashboardStats.recent_reports;

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'HIGH': return 'bg-risk-danger/20 text-risk-danger border-risk-danger/30';
      case 'MEDIUM': return 'bg-risk-warning/20 text-risk-warning border-risk-warning/30';
      case 'LOW': return 'bg-risk-safe/20 text-risk-safe border-risk-safe/30';
      default: return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Audit Reports</h1>
          <p className="text-slate-400">View and download generated analysis reports</p>
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-accent-purple to-accent-blue rounded-xl font-medium shadow-[0_0_15px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] transition-all">
          <FileText className="w-4 h-4" />
          <span>Generate Report</span>
        </button>
      </div>

      <div className="glass-card p-4 flex flex-col md:flex-row justify-between gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search reports..." 
            className="w-full bg-dark-900 border border-slate-700/50 rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-accent-purple/50 focus:ring-1 focus:ring-accent-purple/50"
          />
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 bg-dark-900 border border-slate-700/50 rounded-xl text-sm text-slate-300 hover:bg-dark-800 transition-colors">
          <Filter className="w-4 h-4" />
          <span>Filter</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((report) => (
          <div key={report.id} className="glass-card-hover p-6 flex flex-col">
            <div className="flex justify-between items-start mb-4">
              <div className={`text-xs font-bold px-2 py-1 rounded border ${getRiskBadge(report.overall_risk)}`}>
                {report.overall_risk} RISK
              </div>
              <span className="text-xs text-slate-500">{new Date(report.created_at).toLocaleDateString()}</span>
            </div>
            
            <h3 className="text-lg font-semibold mb-2 line-clamp-2">{report.conversation_title}</h3>
            
            <div className="space-y-2 mb-6 flex-1">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Patterns Found:</span>
                <span className="font-medium text-slate-200">{report.patterns_count}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Confidence:</span>
                <span className="font-medium text-slate-200">{(report.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
            
            <div className="flex space-x-2 mt-auto pt-4 border-t border-slate-700/50">
              <button className="flex-1 py-2 text-sm bg-dark-900 hover:bg-dark-800 rounded-lg transition-colors flex items-center justify-center space-x-2 text-slate-300">
                <FileText className="w-4 h-4" />
                <span>View</span>
              </button>
              <button className="py-2 px-4 text-sm bg-dark-900 hover:bg-dark-800 rounded-lg transition-colors text-accent-blue tooltip-trigger" title="Download PDF">
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
