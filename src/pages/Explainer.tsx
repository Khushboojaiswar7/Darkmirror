import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, BrainCircuit, Activity, BarChart3, AlertTriangle, CheckCircle, Flame, FileCode } from 'lucide-react';
import { mockSampleConversation, mockXAIOutput, mockReasoningTrace } from '../api/mockData';
import { XAIOutput, ReasoningTrace } from '../types';

export const Explainer: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [xaiData, setXaiData] = useState<XAIOutput | null>(mockXAIOutput);
  const [reasoningData, setReasoningData] = useState<ReasoningTrace | null>(mockReasoningTrace);
  const [activeTab, setActiveTab] = useState<'lime' | 'shap' | 'reasoning'>('lime');

  const verdict = mockSampleConversation.analysis_result?.verdict || {
    flag: 1,
    confidence: 0.94,
    verdict_id: 'v-998811',
    risk_level: 'HIGH',
    flagged_message_count: 2,
    total_messages: 4
  };

  const loadOnDemandXAI = () => {
    setLoading(true);
    setTimeout(() => {
      setXaiData(mockXAIOutput);
      setReasoningData(mockReasoningTrace);
      setLoading(false);
    }, 600);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100 flex items-center gap-3">
            <BrainCircuit className="w-8 h-8 text-accent-purple animate-pulse-slow" />
            XAI & Reasoning Explainer
          </h1>
          <p className="text-slate-400 mt-1">
            Explainable AI inspection layer providing LIME weights, SHAP feature attributions, and reasoning trace analysis.
          </p>
        </div>
        <button
          onClick={loadOnDemandXAI}
          disabled={loading}
          className="px-5 py-2.5 rounded-xl gradient-border bg-dark-900 text-slate-100 hover:bg-accent-purple/20 transition-all font-semibold flex items-center gap-2 self-start md:self-auto shadow-lg shadow-accent-purple/10"
        >
          <Sparkles className={`w-4 h-4 text-accent-purple ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Re-computing XAI...' : 'Trigger On-Demand /explain'}
        </button>
      </div>

      {/* Sync Verdict Banner */}
      <div className="glass-card p-6 border-l-4 border-l-risk-danger flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center space-x-4">
          <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${verdict.flag === 1 ? 'bg-risk-danger/20 text-risk-danger' : 'bg-risk-safe/20 text-risk-safe'}`}>
            {verdict.flag === 1 ? <AlertTriangle className="w-6 h-6" /> : <CheckCircle className="w-6 h-6" />}
          </div>
          <div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Classification Verdict</span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${verdict.flag === 1 ? 'risk-danger' : 'risk-safe'}`}>
                {verdict.flag === 1 ? 'FLAGGED (FLAG = 1)' : 'CLEAN (FLAG = 0)'}
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-100 mt-0.5">
              Risk Level: {verdict.risk_level} • Confidence: {(verdict.confidence * 100).toFixed(1)}%
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Verdict ID: <code className="text-accent-purple font-mono">{verdict.verdict_id}</code> • Flagged {verdict.flagged_message_count} of {verdict.total_messages} turns
            </p>
          </div>
        </div>

        {/* Inferred Intent Card */}
        {reasoningData && (
          <div className="bg-dark-900/80 border border-accent-purple/30 rounded-xl p-4 min-w-[240px]">
            <p className="text-xs text-slate-400 font-medium">Async Reasoning Intent</p>
            <p className="text-sm font-bold text-accent-cyan uppercase tracking-wide mt-1">{reasoningData.intent}</p>
            <p className="text-xs text-slate-400 mt-1">
              Deliberate Conf: <span className="text-slate-100 font-semibold">{(reasoningData.deliberate_confidence * 100).toFixed(0)}%</span>
            </p>
          </div>
        )}
      </div>

      {/* Mode Navigation Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('lime')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 ${activeTab === 'lime' ? 'bg-accent-purple/20 text-accent-purple border border-accent-purple/30' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Flame className="w-4 h-4" />
          LIME Token Heatmap
        </button>
        <button
          onClick={() => setActiveTab('shap')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 ${activeTab === 'shap' ? 'bg-accent-purple/20 text-accent-purple border border-accent-purple/30' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <BarChart3 className="w-4 h-4" />
          SHAP Feature Attribution
        </button>
        <button
          onClick={() => setActiveTab('reasoning')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 ${activeTab === 'reasoning' ? 'bg-accent-purple/20 text-accent-purple border border-accent-purple/30' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Activity className="w-4 h-4" />
          Reasoning Trace Chain
        </button>
      </div>

      {/* Tab 1: LIME Weights & Heatmap */}
      {activeTab === 'lime' && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <div className="glass-card p-6 space-y-4">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Flame className="w-5 h-5 text-risk-danger" />
              Token Importance Heatmap (LIME perturbation analysis)
            </h3>
            <p className="text-xs text-slate-400">
              Tokens highlighted in red/amber indicate strong positive weight towards detecting dark manipulation patterns.
            </p>
            <div className="p-5 bg-dark-950/80 rounded-xl border border-slate-800 leading-relaxed text-sm">
              {mockSampleConversation.messages.map((msg, mIdx) => (
                <div key={mIdx} className="mb-4 last:mb-0">
                  <span className={`text-xs font-mono font-bold uppercase mr-2 ${msg.role === 'bot' ? 'text-accent-purple' : 'text-slate-500'}`}>
                    [{msg.role}]:
                  </span>
                  {msg.content.split(' ').map((word, wIdx) => {
                    const cleanWord = word.replace(/[^a-zA-Z]/g, '').toLowerCase();
                    const limeMatch = xaiData?.lime_weights.find(l => l.word.toLowerCase() === cleanWord);
                    const weight = limeMatch ? limeMatch.weight : 0;
                    
                    let bgStyle = '';
                    if (weight > 0.8) bgStyle = 'bg-risk-danger/30 text-rose-300 font-semibold px-1 rounded border border-risk-danger/40';
                    else if (weight > 0.5) bgStyle = 'bg-amber-500/20 text-amber-300 px-1 rounded border border-amber-500/30';
                    else if (weight > 0.2) bgStyle = 'bg-accent-purple/20 text-purple-300 px-1 rounded';

                    return (
                      <span key={wIdx} className={`inline-block mr-1 text-slate-200 transition-all ${bgStyle}`}>
                        {word}
                      </span>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>

          {/* LIME Weight Table */}
          <div className="glass-card p-6">
            <h4 className="text-md font-bold text-slate-100 mb-4">Top Influential Tokens (LIME Weights)</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {xaiData?.lime_weights.map((item, idx) => (
                <div key={idx} className="bg-dark-900/60 p-3 rounded-xl border border-slate-800 flex items-center justify-between">
                  <span className="font-mono text-sm font-semibold text-slate-200">"{item.word}"</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-dark-950 rounded-full h-2 overflow-hidden border border-slate-800">
                      <div className="bg-gradient-to-r from-amber-400 to-risk-danger h-full" style={{ width: `${item.weight * 100}%` }} />
                    </div>
                    <span className="text-xs font-mono font-bold text-accent-purple">{(item.weight * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Tab 2: SHAP Feature Attribution */}
      {activeTab === 'shap' && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6 space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-accent-cyan" />
              SHAP Value Attribution across Agent Modules
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Shapley value distribution calculating the marginal contribution of each detector feature to the final verdict confidence.
            </p>
          </div>

          <div className="space-y-4">
            {Object.entries(xaiData?.shap_values || {}).map(([feature, val], idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-mono text-slate-300">
                  <span>{feature}</span>
                  <span className="text-accent-cyan font-bold">+{(val * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-dark-950 rounded-full h-3 overflow-hidden border border-slate-800">
                  <div
                    className="h-full bg-gradient-to-r from-accent-purple via-accent-blue to-accent-cyan"
                    style={{ width: `${(val / 0.4) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Tab 3: Reasoning Trace Chain */}
      {activeTab === 'reasoning' && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6 space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Activity className="w-5 h-5 text-accent-purple" />
              Async Reasoning-Trace Step Chain
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Triggered automatically post-prediction when FLAG=1 to infer intent and deliberate manipulation confidence.
            </p>
          </div>

          <div className="relative border-l-2 border-accent-purple/30 ml-4 space-y-6 pl-6">
            {reasoningData?.trace.map((step, idx) => (
              <div key={idx} className="relative">
                <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-dark-900 border-2 border-accent-purple flex items-center justify-center text-[10px] font-bold text-accent-purple">
                  {step.step}
                </div>
                <div className="bg-dark-900/60 p-4 rounded-xl border border-slate-800">
                  <span className="text-xs font-mono font-bold text-accent-cyan uppercase tracking-wider">
                    Step {step.step}: {step.action}
                  </span>
                  <p className="text-sm text-slate-200 mt-1">{step.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};
