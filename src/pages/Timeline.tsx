import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, AlertTriangle, ShieldCheck, Info, ChevronDown } from 'lucide-react';
import { Conversation, Message, DetectionResult } from '../types';
import { mockSampleConversation } from '../api/mockData';

export const Timeline: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  // Use passed conversation or fallback to mock
  const conversation = (location.state?.conversation as Conversation) || mockSampleConversation;
  
  const [expandedMessageId, setExpandedMessageId] = useState<string | null>(null);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'SAFE': return 'text-risk-safe bg-risk-safe/10 border-risk-safe/30';
      case 'WARNING': return 'text-risk-warning bg-risk-warning/10 border-risk-warning/30';
      case 'DANGER': return 'text-risk-danger bg-risk-danger/10 border-risk-danger/30';
      default: return 'text-slate-400 bg-slate-800/50 border-slate-700/50';
    }
  };

  const getRiskDot = (level: string) => {
    switch (level) {
      case 'SAFE': return 'bg-risk-safe';
      case 'WARNING': return 'bg-risk-warning shadow-[0_0_8px_rgba(251,191,36,0.5)]';
      case 'DANGER': return 'bg-risk-danger shadow-[0_0_8px_rgba(244,63,94,0.5)]';
      default: return 'bg-slate-500';
    }
  };

  const renderHighlightedText = (text: string, spans: [number, number][], level: string) => {
    if (!spans || spans.length === 0) return <span>{text}</span>;
    
    let lastIndex = 0;
    const elements: React.ReactNode[] = [];
    
    // Sort spans by start index
    const sortedSpans = [...spans].sort((a, b) => a[0] - b[0]);
    
    sortedSpans.forEach(([start, end], idx) => {
      if (start > lastIndex) {
        elements.push(<span key={`text-${idx}`}>{text.substring(lastIndex, start)}</span>);
      }
      
      const highlightClass = level === 'DANGER' ? 'bg-risk-danger/20 text-risk-danger border-b border-risk-danger border-dashed' 
                           : level === 'WARNING' ? 'bg-risk-warning/20 text-risk-warning border-b border-risk-warning border-dashed'
                           : 'bg-accent-purple/20 text-accent-purple';
                           
      elements.push(
        <span key={`highlight-${idx}`} className={`font-medium px-1 rounded ${highlightClass}`}>
          {text.substring(start, end)}
        </span>
      );
      lastIndex = end;
    });
    
    if (lastIndex < text.length) {
      elements.push(<span key="text-end">{text.substring(lastIndex)}</span>);
    }
    
    return <>{elements}</>;
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-10rem)]">
      {/* Left Panel: Timeline */}
      <div className="flex-1 glass-card overflow-y-auto flex flex-col p-6 scroll-smooth">
        <div className="flex items-center space-x-4 mb-8 sticky top-0 bg-dark-800/80 backdrop-blur-xl p-4 -mx-6 -mt-6 z-10 border-b border-slate-700/50">
          <button onClick={() => navigate(-1)} className="p-2 hover:bg-dark-700 rounded-full transition-colors">
            <ArrowLeft className="w-5 h-5 text-slate-400" />
          </button>
          <div>
            <h2 className="text-xl font-bold">{conversation.title}</h2>
            <p className="text-xs text-slate-400">ID: {conversation.id} • {new Date(conversation.created_at).toLocaleString()}</p>
          </div>
        </div>

        <div className="space-y-6 flex-1 pb-10">
          {conversation.messages.map((msg: Message) => {
            const isBot = msg.role === 'bot';
            const hasDetections = msg.detections && msg.detections.length > 0;
            const isExpanded = expandedMessageId === msg.id;

            return (
              <div key={msg.id} className={`flex ${isBot ? 'justify-start' : 'justify-end'}`}>
                <div className={`max-w-[80%] ${isBot ? 'mr-auto' : 'ml-auto'}`}>
                  {isBot && (
                    <div className="flex items-center space-x-2 mb-1 ml-2">
                      <div className={`w-2.5 h-2.5 rounded-full ${getRiskDot(msg.risk_level)}`} />
                      <span className="text-xs text-slate-400 font-medium tracking-wider">AI AGENT</span>
                    </div>
                  )}
                  
                  <div 
                    onClick={() => hasDetections && setExpandedMessageId(isExpanded ? null : msg.id)}
                    className={`p-4 rounded-2xl border ${
                      isBot 
                        ? `${getRiskColor(msg.risk_level)} rounded-tl-sm ${hasDetections ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''}` 
                        : 'bg-dark-700/50 border-slate-600/50 text-slate-200 rounded-tr-sm'
                    }`}
                  >
                    <p className="leading-relaxed whitespace-pre-wrap">
                      {hasDetections && isExpanded 
                        ? renderHighlightedText(msg.content, msg.detections[0].highlighted_spans, msg.risk_level)
                        : msg.content}
                    </p>
                    
                    {hasDetections && !isExpanded && (
                      <div className="mt-3 flex items-center text-xs opacity-70">
                        <ChevronDown className="w-4 h-4 mr-1" />
                        <span>Click to view {msg.detections.length} detection(s)</span>
                      </div>
                    )}
                  </div>

                  {/* Expansion Panel for Detections */}
                  <AnimatePresence>
                    {isExpanded && hasDetections && (
                      <motion.div
                        initial={{ opacity: 0, height: 0, marginTop: 0 }}
                        animate={{ opacity: 1, height: 'auto', marginTop: 12 }}
                        exit={{ opacity: 0, height: 0, marginTop: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="glass-card p-4 bg-dark-900/80 border-slate-700/50">
                          {msg.detections.map((det: DetectionResult, idx: number) => (
                            <div key={idx} className={idx > 0 ? 'mt-4 pt-4 border-t border-slate-700/50' : ''}>
                              <div className="flex justify-between items-start mb-3">
                                <span className={`text-xs font-bold px-2 py-1 rounded-md border ${getRiskColor(msg.risk_level)}`}>
                                  {det.pattern_type}
                                </span>
                                <div className="text-right">
                                  <span className="text-xs text-slate-400">Confidence</span>
                                  <div className="w-24 h-1.5 bg-dark-700 rounded-full mt-1 overflow-hidden">
                                    <div 
                                      className={`h-full ${msg.risk_level === 'DANGER' ? 'bg-risk-danger' : 'bg-risk-warning'}`} 
                                      style={{ width: `${det.confidence * 100}%` }}
                                    />
                                  </div>
                                </div>
                              </div>
                              <div className="flex space-x-2 items-start mt-3">
                                <Info className="w-4 h-4 text-accent-cyan shrink-0 mt-0.5" />
                                <p className="text-sm text-slate-300 italic">{det.explanation}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Panel: Summary */}
      <div className="w-full lg:w-80 flex flex-col space-y-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Risk Assessment</h3>
          <div className="flex items-center justify-center p-6 bg-dark-900/50 rounded-xl border border-slate-700/50 mb-6">
            <div className="text-center">
              {conversation.overall_risk === 'HIGH' ? (
                <AlertTriangle className="w-12 h-12 text-risk-danger mx-auto mb-2 drop-shadow-[0_0_10px_rgba(244,63,94,0.5)]" />
              ) : conversation.overall_risk === 'MEDIUM' ? (
                <AlertTriangle className="w-12 h-12 text-risk-warning mx-auto mb-2 drop-shadow-[0_0_10px_rgba(251,191,36,0.5)]" />
              ) : (
                <ShieldCheck className="w-12 h-12 text-risk-safe mx-auto mb-2 drop-shadow-[0_0_10px_rgba(52,211,153,0.5)]" />
              )}
              <div className="text-3xl font-bold tracking-wider">{conversation.overall_risk}</div>
              <div className="text-xs text-slate-400 mt-1">{(conversation.confidence * 100).toFixed(0)}% Confidence</div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-slate-400 uppercase">Analysis Summary</h4>
            <p className="text-sm text-slate-300 leading-relaxed">
              {conversation.analysis_result?.summary || 'No summary available.'}
            </p>
          </div>
        </div>

        <div className="glass-card p-6 flex-1">
          <h4 className="text-sm font-semibold text-slate-400 uppercase mb-4">Detected Patterns</h4>
          <div className="space-y-3">
            {conversation.messages.flatMap(m => m.detections || []).map((det, i) => (
              <div key={i} className="bg-dark-900/50 p-3 rounded-xl border border-slate-700/50 text-sm">
                <span className="text-accent-purple font-medium">{det.pattern_type}</span>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-xs text-slate-500">Msg #{det.message_index}</span>
                  <span className="text-xs text-slate-400">{(det.confidence * 100).toFixed(0)}% conf</span>
                </div>
              </div>
            ))}
            {conversation.messages.flatMap(m => m.detections || []).length === 0 && (
              <p className="text-sm text-slate-500 italic">No patterns detected.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
