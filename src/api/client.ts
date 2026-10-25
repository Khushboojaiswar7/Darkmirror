import axios from 'axios';
import { useAuthStore } from '../store/authStore';
import { mockDashboardStats, mockEvaluationResult, mockSampleConversation, mockXAIOutput, mockReasoningTrace } from './mockData';
import { DashboardStats, EvaluationResult, Conversation, Dataset, XAIOutput, ReasoningTrace } from '../types';

const IS_DEMO = true; // Fallback to mock data if API is not running

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  auth: {
    login: async () => {
      if (IS_DEMO) return { access_token: 'mock-token', token_type: 'bearer' };
      const res = await apiClient.post('/auth/login');
      return res.data;
    }
  },
  analytics: {
    getDashboard: async (): Promise<DashboardStats> => {
      if (IS_DEMO) return new Promise(resolve => setTimeout(() => resolve(mockDashboardStats), 500));
      try {
        const res = await apiClient.get('/analytics/dashboard');
        return res.data;
      } catch {
        return mockDashboardStats;
      }
    }
  },
  conversations: {
    analyze: async (data: any): Promise<Conversation> => {
      if (IS_DEMO) return new Promise(resolve => setTimeout(() => resolve(mockSampleConversation), 1200));
      try {
        const res = await apiClient.post('/conversations/analyze', data);
        return res.data;
      } catch {
        return mockSampleConversation;
      }
    }
  },
  explain: {
    getExplanation: async (predictionId: string): Promise<XAIOutput> => {
      if (IS_DEMO) return new Promise(resolve => setTimeout(() => resolve(mockXAIOutput), 600));
      try {
        const res = await apiClient.get(`/explain/${predictionId}`);
        return res.data.xai;
      } catch {
        return mockXAIOutput;
      }
    },
    getReasoningTrace: async (predictionId: string): Promise<ReasoningTrace> => {
      if (IS_DEMO) return new Promise(resolve => setTimeout(() => resolve(mockReasoningTrace), 500));
      try {
        const res = await apiClient.get(`/explain/${predictionId}/reasoning`);
        return res.data;
      } catch {
        return mockReasoningTrace;
      }
    }
  },
  audits: {
    createBatch: async (data: { name: string; description?: string; conversations: any[] }) => {
      if (IS_DEMO) return new Promise(resolve => setTimeout(() => resolve({ audit_id: 'batch-101', name: data.name, status: 'COMPLETED', total_conversations: data.conversations.length, flagged_count: 2 }), 1000));
      const res = await apiClient.post('/audits', data);
      return res.data;
    }
  },
  reports: {
    download: async (reportId: string, format: 'json' | 'pdf' | 'csv') => {
      if (IS_DEMO) {
        if (format === 'csv') return 'report_id,overall_risk,confidence\n1,HIGH,0.94';
        return { message: `Simulated ${format.toUpperCase()} download` };
      }
      const res = await apiClient.get(`/reports/${reportId}/download?format=${format}`, { responseType: format === 'pdf' || format === 'csv' ? 'blob' : 'json' });
      return res.data;
    }
  },
  evaluation: {
    run: async (): Promise<EvaluationResult> => {
      if (IS_DEMO) return new Promise(resolve => setTimeout(() => resolve(mockEvaluationResult), 800));
      try {
        const res = await apiClient.post('/evaluation/run');
        return res.data;
      } catch {
        return mockEvaluationResult;
      }
    }
  },
  datasets: {
    list: async (): Promise<Dataset[]> => {
      if (IS_DEMO) return new Promise(resolve => setTimeout(() => resolve([{id: '1', name: 'Sample Dataset', description: 'Sample dataset for demo', conversation_count: 10, created_at: new Date().toISOString()}]), 400));
      try {
        const res = await apiClient.get('/datasets');
        return res.data;
      } catch {
        return [{id: '1', name: 'Sample Dataset', description: 'Sample dataset for demo', conversation_count: 10, created_at: new Date().toISOString()}];
      }
    }
  }
};
