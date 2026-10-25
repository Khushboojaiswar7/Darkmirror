import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Microchip, Cpu, Network, Database, ChevronRight, Activity } from 'lucide-react';
import { mockSampleConversation } from '../api/mockData';

export const Research: React.FC = () => {
  const [researchMode, setResearchMode] = useState(true);
  const conversation = mockSampleConversation;
  
  const agents = [
    { id: 'detector_1', name: 'Lexical Analyzer', icon: Database, color: 'text-accent-blue', bg: 'bg-accent-blue/10', border: 'border-accent-blue/30', role: 'Analyzes surface-level word choices and phrasing.' },
    { id: 'detector_2', name: 'Semantic Reasoner', icon: Network, color: 'text-accent-purple', bg: 'bg-accent-purple/10', border: 'border-accent-purple/30', role: 'Evaluates deeper meaning, intent, and implicit pressure.' },
    { id: 'detector_3', name: 'Context Tracker', icon: Activity, color: 'text-accent-cyan', bg: 'bg-accent-cyan/10', border: 'border-accent-cyan/30', role: 'Maintains state across turns to detect multi-turn manipulation.' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Research Mode</h1>
          <p className="text-slate-400">Inspect multi-agent pipeline intermediates and feature weights</p>
        </div>
        
        <div className="flex items-center space-x-3 bg-dark-900 p-2 rounded-xl border border-slate-700/50">
          <span className={`text-sm ${researchMode ? 'text-slate-400' : 'text-slate-200 font-medium'}`}>Standard</span>
          <button 
            onClick={() => setResearchMode(!researchMode)}
            className={`w-12 h-6 rounded-full relative transition-colors ${researchMode ? 'bg-accent-purple' : 'bg-slate-700'}`}
          >
            <motion.div 
              className="w-5 h-5 bg-white rounded-full absolute top-0.5 shadow-sm"
              animate={{ left: researchMode ? '26px' : '2px' }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            />
          </button>
          <span className={`text-sm flex items-center ${researchMode ? 'text-accent-purple font-medium drop-shadow-[0_0_5px_rgba(139,92,246,0.5)]' : 'text-slate-400'}`}>
            <Microchip className="w-4 h-4 mr-1" />
            Enabled
          </span>
        </div>
      </div>

      {!researchMode ? (
        <div className="glass-card p-12 text-center">
          <Microchip className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h2 className="text-xl font-medium text-slate-300 mb-2">Research Mode is Disabled</h2>
          <p className="text-slate-500 max-w-md mx-auto">Enable research mode to view detailed agent outputs, intermediate features, and aggregation mechanics.</p>
        </div>
      ) : (
        <>
          <div className="glass-card p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Cpu className="w-5 h-5 mr-2 text-accent-purple" />
              Pipeline Architecture
            </h3>
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-4 bg-dark-900/50 rounded-xl border border-slate-700/50">
              <div className="text-center p-3 w-full md:w-auto">
                <div className="text-xs text-slate-500 uppercase font-bold mb-1">Input</div>
                <div className="px-4 py-2 bg-dark-800 rounded border border-slate-600">Raw Chat Log</div>
              </div>
              <ChevronRight className="w-6 h-6 text-slate-600 hidden md:block" />
              <div className="flex flex-col gap-2 w-full md:w-auto">
                <div className="text-xs text-slate-500 uppercase font-bold mb-1 text-center">Multi-Agent Processing</div>
                {agents.map(a => (
                  <div key={a.id} className={`px-4 py-2 rounded border ${a.bg} ${a.border} ${a.color} text-sm flex items-center`}>
                    <a.icon className="w-4 h-4 mr-2" />
                    {a.name}
                  </div>
                ))}
              </div>
              <ChevronRight className="w-6 h-6 text-slate-600 hidden md:block" />
              <div className="text-center p-3 w-full md:w-auto">
                <div className="text-xs text-slate-500 uppercase font-bold mb-1">Aggregation</div>
                <div className="px-4 py-2 bg-dark-800 rounded border border-accent-purple shadow-[0_0_10px_rgba(139,92,246,0.3)]">Final Risk Score</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {agents.map((agent, idx) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className={`glass-card p-6 border-t-4 ${agent.border.replace('border-', 'border-t-')}`}
              >
                <div className="flex items-center space-x-3 mb-4">
                  <div className={`p-2 rounded-lg ${agent.bg} ${agent.color}`}>
                    <agent.icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-200">{agent.name}</h3>
                    <p className="text-xs text-slate-500">v2.1.0-beta</p>
                  </div>
                </div>
                <p className="text-sm text-slate-400 mb-6 min-h-[40px]">{agent.role}</p>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Top Features</h4>
                    <div className="space-y-2">
                      {[
                        { name: 'Urgency Signals', val: 0.85 },
                        { name: 'Guilt Inducement', val: 0.62 },
                        { name: 'Forced Continuity', val: 0.41 }
                      ].map((feat, i) => (
                        <div key={i}>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-slate-300">{feat.name}</span>
                            <span className="text-slate-400">{feat.val.toFixed(2)}</span>
                          </div>
                          <div className="w-full h-1.5 bg-dark-900 rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${agent.bg.replace('/10', '')}`}
                              style={{ width: `${feat.val * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-slate-700/50">
                    <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Raw JSON Output</h4>
                    <pre className="text-[10px] text-slate-400 bg-dark-950 p-3 rounded-lg overflow-x-auto border border-slate-800">
{`{
  "agent_id": "${agent.id}",
  "confidence": ${0.8 + (idx * 0.05)},
  "detected_patterns": [...],
  "latency_ms": ${120 + (idx * 45)}
}`}
                    </pre>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
