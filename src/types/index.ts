// Auth
export interface User { id: string; username: string; email: string; created_at: string; }
export interface AuthResponse { access_token: string; token_type: string; }

// Conversations
export interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
  turn_number: number;
  risk_level: 'SAFE' | 'WARNING' | 'DANGER';
  risk_score: number;
  detections: DetectionResult[];
}

export interface Conversation {
  id: string;
  title: string;
  source_type: string;
  status: string;
  overall_risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'NONE';
  confidence: number;
  messages: Message[];
  analysis_result: PipelineResult | null;
  created_at: string;
}

// Detection & Verdict
export interface DetectionResult {
  message_index: number;
  pattern_type: string;
  confidence: number;
  evidence: string[];
  highlighted_spans: [number, number][];
  explanation: string;
}

export interface AgentOutput {
  agent_name: string;
  results: DetectionResult[];
  intermediate_features: Record<string, any>;
}

export interface Verdict {
  flag: number; // 0 = clean, 1 = flagged
  confidence: number;
  verdict_id: string;
  risk_level: string;
  flagged_message_count: number;
  total_messages: number;
}

export interface ReasoningStep {
  step: number;
  action: string;
  detail: string;
}

export interface ReasoningTrace {
  intent: string;
  deliberate_confidence: number;
  trace: ReasoningStep[];
  pattern_types: string[];
  triggered_signals: string[];
}

export interface LimeWeight {
  word: string;
  weight: number;
  position: number;
}

export interface HeatmapItem {
  position: number;
  intensity: number;
  token: string;
}

export interface XAIOutput {
  lime_weights: LimeWeight[];
  shap_values: Record<string, number>;
  heatmap: HeatmapItem[];
  per_message_explanations?: any[];
}

export interface PipelineResult {
  agents: Record<string, AgentOutput>;
  context_adjustments: any[];
  final_risk: string;
  final_confidence: number;
  per_message_risk: { message_index: number; risk_level: string; risk_score: number; detections: DetectionResult[] }[];
  summary: string;
  verdict?: Verdict;
  reasoning_trace?: ReasoningTrace;
  xai?: XAIOutput;
}

// Analytics
export interface DashboardStats {
  total_conversations: number;
  total_patterns_detected: number;
  average_risk_score: number;
  high_risk_percentage: number;
  pattern_distribution: { name: string; value: number; color: string }[];
  recent_reports: ReportSummary[];
  trend_data: { date: string; conversations: number; avg_risk: number }[];
}

// Reports  
export interface ReportSummary {
  id: string;
  conversation_id: string;
  conversation_title: string;
  overall_risk: string;
  confidence: number;
  patterns_count: number;
  created_at: string;
}

// Evaluation
export interface EvaluationResult {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix: number[][];
  roc_data: { fpr: number[]; tpr: number[]; auc: number };
  comparison?: {
    single_classifier: { accuracy: number; precision: number; recall: number; f1: number };
    multi_agent: { accuracy: number; precision: number; recall: number; f1: number };
  };
}

// Datasets
export interface AnnotatedConversation {
  id: string;
  conversation_text: string;
  labels: Record<string, any>;
  annotator: string;
  approved: boolean;
  created_at: string;
}

export interface Dataset {
  id: string;
  name: string;
  description: string;
  conversation_count: number;
  created_at: string;
}
