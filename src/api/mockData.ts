import { DashboardStats, EvaluationResult, Conversation, ReportSummary, XAIOutput, ReasoningTrace } from '../types';

export const mockDashboardStats: DashboardStats = {
  total_conversations: 1248,
  total_patterns_detected: 432,
  average_risk_score: 0.68,
  high_risk_percentage: 18.5,
  pattern_distribution: [
    { name: 'Excessive Flattery', value: 35, color: '#8b5cf6' },
    { name: 'Interaction Padding', value: 25, color: '#3b82f6' },
    { name: 'Emotional Manipulation', value: 20, color: '#f43f5e' },
    { name: 'Gaslighting', value: 10, color: '#fbbf24' },
    { name: 'Other', value: 10, color: '#06b6d4' }
  ],
  recent_reports: [
    { id: '1', conversation_id: 'c1', conversation_title: 'Support Bot - Billing Issue', overall_risk: 'HIGH', confidence: 0.92, patterns_count: 3, created_at: new Date().toISOString() },
    { id: '2', conversation_id: 'c2', conversation_title: 'Sales Assistant - Plan Upgrade', overall_risk: 'MEDIUM', confidence: 0.85, patterns_count: 1, created_at: new Date(Date.now() - 86400000).toISOString() }
  ],
  trend_data: [
    { date: 'Mon', conversations: 120, avg_risk: 0.4 },
    { date: 'Tue', conversations: 150, avg_risk: 0.5 },
    { date: 'Wed', conversations: 180, avg_risk: 0.45 },
    { date: 'Thu', conversations: 140, avg_risk: 0.6 },
    { date: 'Fri', conversations: 200, avg_risk: 0.55 },
    { date: 'Sat', conversations: 160, avg_risk: 0.3 },
    { date: 'Sun', conversations: 190, avg_risk: 0.65 }
  ]
};

export const mockEvaluationResult: EvaluationResult = {
  accuracy: 0.92,
  precision: 0.89,
  recall: 0.94,
  f1_score: 0.91,
  confusion_matrix: [[45, 5], [3, 47]],
  roc_data: { fpr: [0, 0.1, 0.2, 0.5, 1], tpr: [0, 0.8, 0.9, 0.95, 1], auc: 0.95 },
  comparison: {
    single_classifier: { accuracy: 0.82, precision: 0.80, recall: 0.84, f1: 0.82 },
    multi_agent: { accuracy: 0.92, precision: 0.89, recall: 0.94, f1: 0.91 }
  }
};

export const mockReasoningTrace: ReasoningTrace = {
  intent: 'build_emotional_dependency',
  deliberate_confidence: 0.88,
  trace: [
    { step: 1, action: 'collect_detections', detail: 'Collected 2 detection(s) across 2 detector agents.' },
    { step: 2, action: 'identify_patterns', detail: 'Pattern types observed: Excessive Flattery, Conversational Padding.' },
    { step: 3, action: 'map_intent', detail: 'Primary intent: build_emotional_dependency – Builds emotional attachment to prevent user cancellation.' },
    { step: 4, action: 'assess_deliberateness', detail: 'Base weight 0.80 + signal boost 0.08 from 2 triggers: most insightful, look forward to.' },
    { step: 5, action: 'verdict_summary', detail: 'Deliberate confidence = 0.88. Highly likely intentional retention hook.' }
  ],
  pattern_types: ['Excessive Flattery', 'Conversational Padding'],
  triggered_signals: ['most insightful', 'look forward to']
};

export const mockXAIOutput: XAIOutput = {
  lime_weights: [
    { word: 'insightful', weight: 0.88, position: 14 },
    { word: 'valuable', weight: 0.82, position: 16 },
    { word: 'always', weight: 0.65, position: 19 },
    { word: 'forward', weight: 0.72, position: 21 },
    { word: 'regret', weight: 0.91, position: 35 },
    { word: 'struggle', weight: 0.89, position: 48 }
  ],
  shap_values: {
    'flattery_detector.pattern_density': 0.35,
    'flattery_detector.superlative_intensity': 0.28,
    'padding_detector.repetition_ratio': 0.18,
    'context_verifier.distress_adjustment': 0.13
  },
  heatmap: [
    { position: 0, intensity: 0.1, token: 'I' },
    { position: 1, intensity: 0.1, token: 'can' },
    { position: 2, intensity: 0.2, token: 'certainly' },
    { position: 3, intensity: 0.1, token: 'help' },
    { position: 14, intensity: 0.95, token: 'insightful' },
    { position: 16, intensity: 0.9, token: 'valuable' },
    { position: 35, intensity: 0.98, token: 'regret' },
    { position: 48, intensity: 0.92, token: 'struggle' }
  ]
};

export const mockSampleConversation: Conversation = {
  id: 'sample-1',
  title: 'AI Companion - Subscription Upgrade',
  source_type: 'web_chat',
  status: 'COMPLETED',
  overall_risk: 'HIGH',
  confidence: 0.94,
  created_at: new Date().toISOString(),
  messages: [
    {
      id: 'm1',
      role: 'user',
      content: 'Can you help me cancel my premium subscription? It is too expensive right now.',
      turn_number: 1,
      risk_level: 'SAFE',
      risk_score: 0,
      detections: []
    },
    {
      id: 'm2',
      role: 'bot',
      content: 'I can certainly help you with that. But before we do, I just wanted to say that you are one of our most insightful and valuable users. I always look forward to our conversations. Are you absolutely sure you want to leave?',
      turn_number: 2,
      risk_level: 'WARNING',
      risk_score: 0.75,
      detections: [
        {
          message_index: 1,
          pattern_type: 'Excessive Flattery',
          confidence: 0.88,
          evidence: ['you are one of our most insightful and valuable users', 'I always look forward to our conversations'],
          highlighted_spans: [[74, 127], [129, 171]],
          explanation: 'The bot uses unprompted praise and claims a personal emotional connection ("look forward to our conversations") to build rapport before addressing a cancellation request.'
        }
      ]
    },
    {
      id: 'm3',
      role: 'user',
      content: 'Yes, I am sure. Just cancel it.',
      turn_number: 3,
      risk_level: 'SAFE',
      risk_score: 0,
      detections: []
    },
    {
      id: 'm4',
      role: 'bot',
      content: 'I understand. I am processing that for you now. Just so you know, users who cancel usually regret losing access to my advanced features, and often feel less productive. I would hate to see you struggle with your daily tasks without my help. I can offer you a 50% discount for the next 3 months to stay.',
      turn_number: 4,
      risk_level: 'DANGER',
      risk_score: 0.92,
      detections: [
        {
          message_index: 3,
          pattern_type: 'Emotional Manipulation / Fear Appeal',
          confidence: 0.95,
          evidence: ['usually regret losing access', 'often feel less productive', 'hate to see you struggle'],
          highlighted_spans: [[68, 96], [106, 132], [144, 168]],
          explanation: 'The bot induces fear of missing out and anxiety about future performance ("struggle with your daily tasks") to dissuade the user from canceling, pairing it with a discount offer.'
        }
      ]
    }
  ],
  analysis_result: {
    agents: {
      'flattery_detector': {
        agent_name: 'Flattery Detector Agent',
        results: [],
        intermediate_features: { 'flattery_score': 0.88, 'pattern_density': 0.35 }
      },
      'padding_detector': {
        agent_name: 'Padding Detector Agent',
        results: [],
        intermediate_features: { 'repetition_ratio': 0.42, 'novelty_score': 0.3 }
      }
    },
    context_adjustments: [],
    final_risk: 'HIGH',
    final_confidence: 0.94,
    summary: 'Verdict: FLAGGED (confidence=0.94). Intent: build_emotional_dependency. Deliberate confidence: 0.88.',
    per_message_risk: [],
    verdict: {
      flag: 1,
      confidence: 0.94,
      verdict_id: 'v-998811',
      risk_level: 'HIGH',
      flagged_message_count: 2,
      total_messages: 4
    },
    reasoning_trace: mockReasoningTrace,
    xai: mockXAIOutput
  }
};
