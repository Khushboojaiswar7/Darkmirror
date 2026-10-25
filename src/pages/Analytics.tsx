import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar, Legend } from 'recharts';
import { mockDashboardStats } from '../api/mockData';

export const Analytics: React.FC = () => {
  const triggerPhrases = [
    { phrase: "limited time offer", count: 142 },
    { phrase: "other users are looking", count: 98 },
    { phrase: "you're one of our best", count: 87 },
    { phrase: "don't miss out", count: 76 },
    { phrase: "only 2 left", count: 65 },
    { phrase: "special discount just for you", count: 54 },
    { phrase: "you might regret", count: 43 },
    { phrase: "are you absolutely sure", count: 32 }
  ];

  const confidenceData = [
    { name: 'Average Confidence', value: 85, fill: '#8b5cf6' }
  ];

  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Workspace Analytics</h1>
        <p className="text-slate-400">Deep dive into dark pattern trends and metrics</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pattern Frequency Bar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold mb-6">Pattern Frequency</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockDashboardStats.pattern_distribution} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="name" type="category" width={150} stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem' }}
                  cursor={{ fill: '#1e293b' }}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {mockDashboardStats.pattern_distribution.map((entry, index) => (
                    <cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Trigger Phrases */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6 flex flex-col"
        >
          <h3 className="text-lg font-semibold mb-6">Common Trigger Phrases</h3>
          <div className="flex-1 overflow-y-auto pr-2 space-y-3">
            {triggerPhrases.map((item, idx) => (
              <div key={idx} className="flex items-center">
                <div className="w-full bg-dark-900 rounded-full h-8 flex items-center relative overflow-hidden">
                  <div 
                    className="absolute left-0 top-0 bottom-0 bg-accent-purple/20 border-r border-accent-purple/50 rounded-r-full" 
                    style={{ width: `${(item.count / triggerPhrases[0].count) * 100}%` }}
                  />
                  <div className="relative z-10 flex justify-between w-full px-4 text-sm">
                    <span className="text-slate-200 font-medium">"{item.phrase}"</span>
                    <span className="text-slate-400">{item.count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Confidence Gauge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card p-6 flex flex-col items-center justify-center"
        >
          <h3 className="text-lg font-semibold mb-2 self-start w-full">Model Confidence</h3>
          <div className="h-[250px] w-full flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart 
                cx="50%" cy="50%" 
                innerRadius="70%" outerRadius="90%" 
                barSize={20} data={confidenceData}
                startAngle={180} endAngle={0}
              >
                <RadialBar
                  background={{ fill: '#1e293b' }}
                  dataKey="value"
                  cornerRadius={10}
                />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/4 text-center">
              <div className="text-4xl font-bold text-slate-100">{confidenceData[0].value}%</div>
              <div className="text-xs text-slate-400 mt-1">Average</div>
            </div>
          </div>
        </motion.div>
        
        {/* Risk Over Time Chart Placeholder */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold mb-6">Risk Over Conversation Turn</h3>
          <div className="h-[250px] flex items-center justify-center border border-dashed border-slate-700/50 rounded-xl">
            <p className="text-slate-500 text-sm">Select a specific conversation to view turn-by-turn risk analysis.</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
