export type Condition = "memory" | "personality" | "values" | "goals" | "model" | "progressive";

export interface Experiment {
  id: string;
  baseline: string;
  variant: string;
  condition: Condition;
  transformation_percentage: number;
  model: string;
  blind_condition: number;
  trial_count: number;
  random_seed: number | null;
  prompt_version: string;
  is_demo: number;
  created_at: string;
  status: string;
  identity_score_mean: number | null;
  confidence_mean: number | null;
}

export interface CurvePoint {
  transformation_percentage: number;
  ics: number;
}

export interface IdentityBoundary {
  has_sufficient_data: boolean;
  identity_boundary_from_pct?: number;
  identity_boundary_to_pct?: number;
  identity_boundary_drop?: number;
  total_decline?: number;
  phase_transition_detected: boolean;
  message: string;
}

export interface AnalysisResponse {
  condition: string;
  model: string;
  curve: CurvePoint[];
  identity_boundary: IdentityBoundary;
  perspective_consistency_score: number | null;
}

export interface ModelsResponse {
  ollama_available: boolean;
  models: string[];
  demo_mode_recommended: boolean;
  error?: string;
}

export interface RunResult {
  experiment_id?: string;
  status: string;
  results?: { run_id: string; ok: boolean; error?: string; parse_failed?: boolean }[];
  estimated_calls?: number;
  model?: string;
}

export interface ScoreDetail {
  id: string;
  same_entity: number | null;
  identity_score: number | null;
  confidence: number | null;
  primary_identity_property: string | null;
  reason: string | null;
}

export interface ResponseDetail {
  id: string;
  raw_response: string | null;
  parsed_json: string;
  parse_failed: number;
  latency_ms: number | null;
}

export interface RunDetail {
  id: string;
  trial_index: number;
  question_id: string;
  question_text: string;
  perspective: string;
  response: ResponseDetail | null;
  score: ScoreDetail | null;
}

export interface ExperimentDetail {
  experiment: Experiment;
  runs: RunDetail[];
}
