export interface User {
  id: string;
  email: string;
  team_name?: string;
  full_name?: string;
  role: 'admin' | 'analyst' | 'coach';
  subscription_tier: 'free' | 'pro' | 'enterprise';
  referral_source?: string;  
  created_at: string;
}

export interface Video {
  id: string;
  user_id: string;
  filename: string;
  title?: string;
  description?: string;
  s3_url?: string;
  duration?: number;
  status: 'uploaded' | 'processing' | 'ready' | 'error';
  analysis_intent?: AnalysisIntent;
  upload_progress: number;  // 0-100 percentage
  processing_priority: 'low' | 'standard' | 'high' | 'enterprise';
  file_size?: number;
  content_type?: string;
  error_message?: string;
  created_at: string;
}

export interface Analysis {
  id: string;
  video_id: string;
  openstarlab_results?: OpenStarLabResults;
  ai_insights?: AIInsights;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  processing_time?: number;
  progress_percentage: number;  // 0-100 percentage
  current_step?: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  created_at: string;
}

// OpenStarLab Intelligence Types
export interface OpenStarLabResults {
  events: DetectedEvent[];
  tactical_analysis: TacticalAnalysis;
  player_evaluations: PlayerEvaluations;
  predictions: PredictiveInsights;
  confidence_scores: ConfidenceScores;
  processing_metadata: ProcessingMetadata;
}

export interface DetectedEvent {
  id: string;
  timestamp: number;
  formatted_time: string;
  event_type: string;
  confidence: number;
  coordinates: {
    x: number;
    y: number;
    zone?: string;
  };
  players_involved: PlayerInvolved[];
  team: 'home' | 'away';
  context?: {
    phase_of_play: string;
    pressure_level: string;
    field_tilt: number;
  };
}

export interface PlayerInvolved {
  player_id: string;
  jersey_number: number;
  position: string;
  team: 'home' | 'away';
  role: 'primary' | 'secondary';
  confidence: number;
  name?: string;
}

export interface TacticalAnalysis {
  formations: {
    home_team: FormationAnalysis;
    away_team: FormationAnalysis;
    formation_changes: FormationChange[];
  };
  possession_analysis: {
    possession_sequences: PossessionSequence[];
    field_tilt: FieldTilt;
    tempo_analysis: TempoAnalysis;
  };
  strategic_insights: StrategicInsight[];
  hpus_metrics: HPUSMetrics;
}

export interface FormationAnalysis {
  primary_formation: string;
  confidence: number;
  formation_stability: number;
  tactical_discipline: number;
  avg_positions: Record<string, { x: number; y: number; spread: number }>;
}

export interface FormationChange {
  timestamp: number;
  team: 'home' | 'away';
  from_formation: string;
  to_formation: string;
  trigger_event: string;
  confidence: number;
}

export interface PossessionSequence {
  sequence_id: string;
  duration: number;
  passes_count: number;
  team: 'home' | 'away';
  start_zone: string;
  end_zone: string;
  outcome: string;
  xg_value: number;
}

export interface FieldTilt {
  overall_tilt: number;
  attacking_tilt: number;
  defensive_tilt: number;
  neutral_play: number;
}

export interface TempoAnalysis {
  overall_tempo: number;
  tempo_variations: {
    first_half: number;
    second_half: number;
  };
  high_intensity_periods: IntensityPeriod[];
}

export interface IntensityPeriod {
  start_time: number;
  duration: number;
  intensity_level: number;
  trigger: string;
}

export interface StrategicInsight {
  insight_type: string;
  title: string;
  description: string;
  confidence: number;
  actionable_recommendation: string;
  supporting_metrics: Record<string, any>;
}

export interface HPUSMetrics {
  overall_hpus: number;
  attacking_hpus: number;
  defensive_hpus: number;
  pressure_situations: {
    high_press_success_rate: number;
    counter_press_efficiency: number;
    pressure_recovery_time: number;
  };
}

export interface PlayerEvaluations {
  player_metrics: Record<string, PlayerMetrics>;
  performance_insights: PerformanceInsight[];
  team_cohesion_metrics: TeamCohesionMetrics;
}

export interface PlayerMetrics {
  player_id: string;
  jersey_number: number;
  position: string;
  team: 'home' | 'away';
  overall_performance_score: number;
  performance_grade: string;
  total_actions: number;
  action_breakdown: Record<string, {
    count: number;
    avg_q_value: number;
    success_rate: number;
  }>;
  situational_performance: Record<string, number>;
  consistency_score: number;
  clutch_performance: number;
  team_contribution: number;
}

export interface PerformanceInsight {
  insight_type: string;
  title: string;
  description: string;
  confidence: number;
  player_id?: string;
  performance_score?: number;
}

export interface TeamCohesionMetrics {
  home_team_cohesion: number;
  away_team_cohesion: number;
  pass_network_density: number;
  positional_coordination: number;
  tactical_synchronization: number;
}

export interface PredictiveInsights {
  match_outcomes: MatchOutcomePredictions;
  tactical_scenarios: TacticalScenarioPredictions;
  player_performance: PlayerPerformancePredictions;
  formation_effectiveness: FormationEffectivenessPredictions;
}

export interface MatchOutcomePredictions {
  final_score_predictions: ScorePrediction[];
  match_events_predictions: {
    total_goals: { predicted: number; confidence: number };
    total_cards: { predicted: number; confidence: number };
    corner_kicks: { predicted: number; confidence: number };
  };
  comeback_probability: {
    comeback_team: 'home' | 'away' | null;
    goal_deficit: number;
    comeback_probability: number;
    confidence: number;
  };
}

export interface ScorePrediction {
  scoreline: string;
  probability: number;
  confidence: number;
}

export interface TacticalScenarioPredictions {
  formation_changes: FormationChangePrediction[];
  tactical_adjustments: TacticalAdjustment[];
  substitution_impact: SubstitutionImpact;
}

export interface FormationChangePrediction {
  predicted_time: number;
  team: 'home' | 'away';
  current_formation: string;
  predicted_formation: string;
  probability: number;
  expected_impact: 'positive' | 'neutral' | 'negative';
  confidence: number;
}

export interface TacticalAdjustment {
  adjustment_type: string;
  predicted_change: string;
  probability: number;
  expected_effectiveness: number;
  confidence: number;
}

export interface SubstitutionImpact {
  optimal_substitution_time: number;
  predicted_substitutions: number;
  impact_predictions: {
    substitution_type: string;
    expected_impact: number;
    probability_of_goal_contribution?: number;
    confidence: number;
  }[];
}

export interface PlayerPerformancePredictions {
  performance_trends: Record<string, {
    current_score: number;
    predicted_trend: 'improving' | 'stable' | 'declining';
    trend_magnitude: number;
    confidence: number;
  }>;
  fatigue_predictions: Record<string, {
    current_fatigue: number;
    predicted_drop_off_time: number;
    performance_impact: number;
    confidence: number;
  }>;
  impact_players: {
    player_id: string;
    impact_score: number;
    predicted_contribution: number;
  }[];
  substitution_candidates: {
    player_id: string;
    reason: 'fatigue' | 'performance';
    urgency: 'high' | 'medium';
  }[];
}

export interface FormationEffectivenessPredictions {
  current_formation_effectiveness: Record<string, {
    formation: string;
    predicted_effectiveness: number;
    strengths: string[];
    weaknesses: string[];
    confidence: number;
  }>;
  alternative_formation_analysis: Record<string, {
    formation: string;
    predicted_effectiveness: number;
    expected_improvement: number;
    confidence: number;
  }[]>;
}

export interface ConfidenceScores {
  overall_intelligence_confidence: number;
  event_detection_confidence: number;
  tactical_analysis_confidence: number;
  player_evaluation_confidence: number;
  predictive_modeling_confidence: number;
  data_completeness_score: number;
}

export interface ProcessingMetadata {
  pipeline_version: string;
  total_processing_time: number;
  analysis_intent: string;
  events_processed: number;
  players_evaluated: number;
  tactical_insights_generated: number;
  predictions_generated: number;
  data_quality_score: number;
}

export interface AIInsights {
  tactical_insights: StrategicInsight[];
  player_insights: PerformanceInsight[];
  key_recommendations: Recommendation[];
  performance_summary: {
    events_detected: number;
    tactical_patterns_identified: number;
    standout_performances: number;
    overall_match_quality: number;
  };
  predictive_insights: {
    match_outcome_predictions: MatchOutcomePredictions;
    tactical_recommendations: TacticalScenarioPredictions;
    player_performance_predictions: PlayerPerformancePredictions;
  };
}

export interface Recommendation {
  type: 'tactical' | 'player_performance' | 'formation' | 'strategic';
  title: string;
  recommendation: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
}

export interface Export {
  id: string;
  analysis_id: string;
  export_type: 'video_clips' | 'pdf_report' | 'csv_data' | 'full_package';
  file_path?: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  created_at: string;
}

export type AnalysisIntent = 
  | 'individual_player'
  | 'tactical_phase'
  | 'opposition_scouting'
  | 'set_piece'
  | 'full_match';

export interface AnalysisIntentConfig {
  value: AnalysisIntent;
  label: string;
  description: string;
  estimatedTime: string;
  features: string[];
}

export interface UploadProgress {
  progress: number;
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  message?: string;
}

export interface DashboardStats {
  totalVideos: number;
  totalAnalyses: number;
  avgProcessingTime: number;
  completedAnalyses: number;
  pendingAnalyses: number;
  recentActivity: Array<{
    id: string;
    type: 'upload' | 'analysis' | 'export';
    description: string;
    timestamp: string;
  }>;
}