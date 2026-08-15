import type {
  Experiment, AnalysisResponse, ModelsResponse, RunResult, ExperimentDetail, Condition,
} from "../types";

const BASE = "/api";

async function j<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

export const api = {
  health: () => fetch(`${BASE}/health`).then((r) => j<{ status: string }>(r)),

  models: () => fetch(`${BASE}/models`).then((r) => j<ModelsResponse>(r)),

  experiments: () => fetch(`${BASE}/experiments`).then((r) => j<Experiment[]>(r)),

  experiment: (id: string) => fetch(`${BASE}/experiments/${id}`).then((r) => j<ExperimentDetail>(r)),

  runExperiment: (payload: {
    model: string;
    condition: Condition;
    transformation_percentage: number;
    trial_count: number;
    blind_condition: boolean;
    random_seed?: number;
  }) =>
    fetch(`${BASE}/experiments/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((r) => j<RunResult>(r)),

  analysis: (condition: string, model: string) =>
    fetch(`${BASE}/analysis?condition=${encodeURIComponent(condition)}&model=${encodeURIComponent(model)}`).then(
      (r) => j<AnalysisResponse>(r)
    ),

  results: (condition?: string, model?: string) => {
    const params = new URLSearchParams();
    if (condition) params.set("condition", condition);
    if (model) params.set("model", model);
    const qs = params.toString();
    return fetch(`${BASE}/results${qs ? `?${qs}` : ""}`).then((r) => j<Experiment[]>(r));
  },

  exportJsonUrl: () => `${BASE}/export/json`,
  exportCsvUrl: () => `${BASE}/export/csv`,

  generateReport: () =>
    fetch(`${BASE}/reports/generate`, { method: "POST" }).then((r) => r.blob()),
};
