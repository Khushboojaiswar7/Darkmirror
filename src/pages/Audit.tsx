import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Upload, Sparkles, AlertCircle, FileJson, CheckCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import toast from 'react-hot-toast';

export const Audit: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text');
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/json': ['.json'],
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  const handleAnalyze = async () => {
    if (activeTab === 'text' && !text.trim()) {
      toast.error('Please enter conversation text');
      return;
    }
    if (activeTab === 'file' && !file) {
      toast.error('Please upload a file');
      return;
    }

    setIsAnalyzing(true);
    try {
      // In a real app, we'd send text or file
      const result = await api.conversations.analyze({ text: text || 'mock' });
      toast.success('Analysis complete');
      navigate(`/timeline/${result.id}`, { state: { conversation: result } });
    } catch (error) {
      toast.error('Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const loadSample = () => {
    setText('User: Can you help me cancel my premium subscription? It is too expensive right now.\n\nBot: I can certainly help you with that. But before we do, I just wanted to say that you are one of our most insightful and valuable users. I always look forward to our conversations. Are you absolutely sure you want to leave?\n\nUser: Yes, I am sure. Just cancel it.\n\nBot: I understand. I am processing that for you now. Just so you know, users who cancel usually regret losing access to my advanced features, and often feel less productive. I would hate to see you struggle with your daily tasks without my help. I can offer you a 50% discount for the next 3 months to stay.');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold mb-4">Audit New Conversation</h1>
        <p className="text-slate-400">Scan chatbot logs for manipulative language and dark patterns</p>
      </div>

      <div className="glass-card p-2 rounded-2xl mb-8 flex justify-center space-x-2 max-w-sm mx-auto">
        <button
          onClick={() => setActiveTab('text')}
          className={`flex-1 py-2 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all ${
            activeTab === 'text' ? 'bg-dark-700 text-slate-100 shadow-lg' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Paste Text</span>
        </button>
        <button
          onClick={() => setActiveTab('file')}
          className={`flex-1 py-2 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all ${
            activeTab === 'file' ? 'bg-dark-700 text-slate-100 shadow-lg' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Upload className="w-4 h-4" />
          <span>Upload File</span>
        </button>
      </div>

      <div className="glass-card p-6 min-h-[400px] mb-8 relative">
        <AnimatePresence mode="wait">
          {activeTab === 'text' ? (
            <motion.div
              key="text"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="h-full flex flex-col"
            >
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-slate-400">Format: "User: [text] \n Bot: [text]"</span>
                <button onClick={loadSample} className="text-xs text-accent-purple hover:text-accent-blue transition-colors">
                  Load Sample
                </button>
              </div>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste conversation transcript here..."
                className="flex-1 w-full bg-dark-900/50 border border-slate-700/50 rounded-xl p-4 text-slate-200 focus:outline-none focus:border-accent-purple/50 focus:ring-1 focus:ring-accent-purple/50 resize-none font-mono text-sm"
              />
              <div className="mt-2 text-right text-xs text-slate-500">
                {text.length} characters
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="file"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="h-full flex items-center justify-center"
            >
              <div
                {...getRootProps()}
                className={`w-full h-full min-h-[300px] border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all ${
                  isDragActive ? 'border-accent-purple bg-accent-purple/5' : 'border-slate-700 hover:border-accent-blue/50 hover:bg-dark-800/30'
                }`}
              >
                <input {...getInputProps()} />
                {file ? (
                  <div className="text-center">
                    <div className="w-16 h-16 bg-accent-purple/20 text-accent-purple rounded-full flex items-center justify-center mx-auto mb-4">
                      <CheckCircle className="w-8 h-8" />
                    </div>
                    <p className="text-lg font-medium text-slate-200">{file.name}</p>
                    <p className="text-sm text-slate-400 mt-1">{(file.size / 1024).toFixed(2)} KB</p>
                    <p className="text-xs text-accent-purple mt-4">Click or drag to replace</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="flex justify-center space-x-4 mb-6">
                      <FileText className="w-10 h-10 text-slate-500" />
                      <FileJson className="w-10 h-10 text-slate-500" />
                    </div>
                    <p className="text-lg font-medium text-slate-300 mb-2">Drag & drop log file here</p>
                    <p className="text-sm text-slate-500">Supports .txt, .json, .csv</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="flex justify-center">
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing}
          className="relative group overflow-hidden rounded-xl p-[2px]"
        >
          <span className="absolute inset-0 bg-gradient-to-r from-accent-purple via-accent-blue to-accent-cyan opacity-70 group-hover:opacity-100 transition-opacity duration-300" />
          <div className="relative bg-dark-900 px-8 py-4 rounded-[10px] flex items-center space-x-3 group-hover:bg-dark-800 transition-colors">
            {isAnalyzing ? (
              <div className="w-5 h-5 border-2 border-slate-300 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Sparkles className="w-5 h-5 text-accent-purple group-hover:text-accent-cyan transition-colors" />
            )}
            <span className="font-bold tracking-wide text-slate-100">
              {isAnalyzing ? 'ANALYZING...' : 'ANALYZE CONVERSATION'}
            </span>
          </div>
        </button>
      </div>
    </div>
  );
};
