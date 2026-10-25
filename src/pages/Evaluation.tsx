import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Upload, TrendingUp, Target, Activity, FileCheck2 } from 'lucide-react';
import { mockEvaluationResult } from '../api/mockData';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export const Evaluation: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [hasResults, setHasResults] = useState(true); // Default true for demo
  const results = mockEvaluationResult;

  const handleRun = () => {
    setIsRunning(true);
    setTimeout(() => {
      setIsRunning(false);
      setHasResults(true);
    }, 2000);
  };

  // Format ROC data for recharts
  const rocChartData = results.roc_data.fpr.map((fpr, idx) => ({
    fpr: fpr * 100,
    tpr: results.roc_data.tpr[idx] * 100,
  }));

  const metrics = [
    { label: 'Accuracy', value: results.accuracy, icon: Target, color: 'text-accent-purple' },
    { label: 'Precision', value: results.precision, icon: TrendingUp, color: 'text-accent-blue' },
    { label: 'Recall', value: results.recall, icon: Activity, color: 'text-accent-cyan' },
    { label: 'F1 Score', value: results.f1_score, icon: FileCheck2, color: 'text-risk-safe' },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-2">Model Evaluation</h1>
          <p className="text-slate-400">Benchmark detection models against labeled datasets</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 glass-card hover:bg-dark-800 transition-colors">
            <Upload className="w-4 h-4 text-slate-400" />
            <span className="text-sm">Upload Dataset</span>
          </button>
          <button 
            onClick={handleRun}
            disabled={isRunning}
            className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-accent-purple to-accent-blue rounded-xl font-medium shadow-[0_0_15px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] transition-all disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isRunning ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>{isRunning ? 'Running...' : 'Run Evaluation'}</span>
          </button>
        </div>
      </div>

      {hasResults && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* Metrics row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {metrics.map((m, idx) => (
              <motion.div 
                key={m.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="glass-card p-6 flex flex-col items-center justify-center text-center relative overflow-hidden group"
              >
                <div className={`absolute -right-4 -top-4 w-16 h-16 rounded-full bg-current opacity-5 group-hover:scale-150 transition-transform duration-500 ${m.color}`} />
                <m.icon className={`w-8 h-8 mb-3 ${m.color}`} />
                <div className="text-3xl font-bold mb-1">{(m.value * 100).toFixed(1)}%</div>
                <div className="text-sm text-slate-400 uppercase tracking-wider">{m.label}</div>
              </motion.div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* ROC Curve */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-6 flex justify-between">
                <span>ROC Curve</span>
                <span className="text-sm font-normal text-accent-purple bg-accent-purple/10 px-2 py-1 rounded">AUC: {results.roc_data.auc.toFixed(3)}</span>
              </h3>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={rocChartData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                    <defs>
                      <linearGradient id="colorRoc" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="fpr" stroke="#94a3b8" type="number" domain={[0, 100]} />
                    <YAxis stroke="#94a3b8" type="number" domain={[0, 100]} />
                    <Tooltip 
                      formatter={(val: number) => [`${val.toFixed(1)}%`, '']} 
                      labelFormatter={(label) => `FPR: ${Number(label).toFixed(1)}%`}
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem' }}
                    />
                    <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 100, y: 100 }]} stroke="#64748b" strokeDasharray="3 3" />
                    <Area type="monotone" dataKey="tpr" stroke="#8b5cf6" strokeWidth={3} fillOpacity={1} fill="url(#colorRoc)" name="TPR" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Confusion Matrix */}
            <div className="glass-card p-6 flex flex-col">
              <h3 className="text-lg font-semibold mb-6">Confusion Matrix</h3>
              <div className="flex-1 flex flex-col items-center justify-center">
                <div className="grid grid-cols-3 gap-2 text-center w-full max-w-sm">
                  <div className="col-span-1"></div>
                  <div className="col-span-1 text-sm text-slate-400 font-medium">Pred Negative</div>
                  <div className="col-span-1 text-sm text-slate-400 font-medium">Pred Positive</div>
                  
                  <div className="col-span-1 text-sm text-slate-400 font-medium flex items-center justify-end pr-4">True Negative</div>
                  <div className="col-span-1 bg-dark-900 border border-slate-700/50 rounded-xl p-6 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-risk-safe/10" />
                    <span className="relative z-10 text-2xl font-bold">{results.confusion_matrix[0][0]}</span>
                    <div className="relative z-10 text-xs text-slate-500 mt-1">TN</div>
                  </div>
                  <div className="col-span-1 bg-dark-900 border border-slate-700/50 rounded-xl p-6 relative overflow-hidden">
                    <div className="absolute inset-0 bg-risk-danger/20" />
                    <span className="relative z-10 text-2xl font-bold text-risk-danger">{results.confusion_matrix[0][1]}</span>
                    <div className="relative z-10 text-xs text-slate-500 mt-1">FP</div>
                  </div>
                  
                  <div className="col-span-1 text-sm text-slate-400 font-medium flex items-center justify-end pr-4">True Positive</div>
                  <div className="col-span-1 bg-dark-900 border border-slate-700/50 rounded-xl p-6 relative overflow-hidden">
                    <div className="absolute inset-0 bg-risk-danger/20" />
                    <span className="relative z-10 text-2xl font-bold text-risk-danger">{results.confusion_matrix[1][0]}</span>
                    <div className="relative z-10 text-xs text-slate-500 mt-1">FN</div>
                  </div>
                  <div className="col-span-1 bg-dark-900 border border-slate-700/50 rounded-xl p-6 relative overflow-hidden">
                    <div className="absolute inset-0 bg-accent-purple/20" />
                    <span className="relative z-10 text-2xl font-bold text-accent-purple">{results.confusion_matrix[1][1]}</span>
                    <div className="relative z-10 text-xs text-slate-500 mt-1">TP</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Comparison Table */}
          {results.comparison && (
            <div className="glass-card p-6 overflow-x-auto">
              <h3 className="text-lg font-semibold mb-4">Architecture Comparison</h3>
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50 text-slate-400">
                    <th className="pb-3 font-medium">Architecture</th>
                    <th className="pb-3 font-medium">Accuracy</th>
                    <th className="pb-3 font-medium">Precision</th>
                    <th className="pb-3 font-medium">Recall</th>
                    <th className="pb-3 font-medium">F1 Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  <tr className="text-slate-300">
                    <td className="py-4">Single Classifier Baseline</td>
                    <td className="py-4">{(results.comparison.single_classifier.accuracy * 100).toFixed(1)}%</td>
                    <td className="py-4">{(results.comparison.single_classifier.precision * 100).toFixed(1)}%</td>
                    <td className="py-4">{(results.comparison.single_classifier.recall * 100).toFixed(1)}%</td>
                    <td className="py-4">{(results.comparison.single_classifier.f1 * 100).toFixed(1)}%</td>
                  </tr>
                  <tr className="bg-accent-purple/5 text-slate-100 font-medium relative">
                    <td className="py-4 pl-4 rounded-l-lg border-l-4 border-accent-purple">Multi-Agent Framework (Ours)</td>
                    <td className="py-4 text-risk-safe">+ {((results.comparison.multi_agent.accuracy - results.comparison.single_classifier.accuracy) * 100).toFixed(1)}%</td>
                    <td className="py-4 text-risk-safe">+ {((results.comparison.multi_agent.precision - results.comparison.single_classifier.precision) * 100).toFixed(1)}%</td>
                    <td className="py-4 text-risk-safe">+ {((results.comparison.multi_agent.recall - results.comparison.single_classifier.recall) * 100).toFixed(1)}%</td>
                    <td className="py-4 text-risk-safe rounded-r-lg">+ {((results.comparison.multi_agent.f1 - results.comparison.single_classifier.f1) * 100).toFixed(1)}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};
