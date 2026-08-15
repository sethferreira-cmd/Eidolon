import { useEffect, useState, useCallback } from "react";
import { Header } from "./components/Header";
import { Panel, StatCard, DemoBadge } from "./components/Panel";
import { IdentityCurveChart } from "./components/IdentityCurveChart";
import { ExperimentRunner } from "./components/ExperimentRunner";
import { ResultsTable } from "./components/ResultsTable";
import { api } from "./services/api";
import type { AnalysisResponse, Experiment, ModelsResponse, Condition } from "./types";

const CONDITIONS: Condition[] = ["memory", "personality", "values", "goals", "model", "progressive"];

function App() {
  const [modelsInfo, setModelsInfo] = useState<ModelsResponse | null>(null);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [condition, setCondition] = useState<Condition>("memory");
  const [selectedModel, setSelectedModel] = useState<string>("demo-model");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const refreshExperiments = useCallback(() => {
    api.experiments().then(setExperiments).catch((e) => setLoadError(String(e)));
  }, []);

  useEffect(() => {
    api.models().then(setModelsInfo).catch(() => setModelsInfo({ ollama_available: false, models: [], demo_mode_recommended: true }));
    refreshExperiments();
  }, [refreshExperiments]);

  useEffect(() => {
    if (!selectedModel) return;
    api.analysis(condition, selectedModel).then(setAnalysis).catch(() => setAnalysis(null));
  }, [condition, selectedModel]);

  const knownModels = Array.from(new Set(experiments.map((e) => e.model)));
  const isDemoSelected = selectedModel === "demo-model" || experiments.find((e) => e.model === selectedModel)?.is_demo === 1;

  const overallIcsValues = experiments
    .filter((e) => e.identity_score_mean !== null)
    .map((e) => e.identity_score_mean as number);
  const meanIcs = overallIcsValues.length
    ? (overallIcsValues.reduce((a, b) => a + b, 0) / overallIcsValues.length).toFixed(1)
    : "—";

  return (
    <div className="min-h-screen bg-[var(--color-ink)]">
      <Header ollamaAvailable={modelsInfo?.ollama_available ?? null} />

      <main className="max-w-6xl mx-auto px-8 py-8 flex flex-col gap-8">
        {modelsInfo?.demo_mode_recommended && (
          <div className="border border-[var(--color-amber-dim)] bg-[var(--color-panel)] rounded-sm px-4 py-3 flex items-center justify-between">
            <div className="font-mono text-xs text-[var(--color-text-dim)]">
              {modelsInfo.ollama_available
                ? "Ollama is connected but no models are installed."
                : "Ollama isn't running or installed."}{" "}
              You're viewing Demo Mode — synthetic data only.
            </div>
            <DemoBadge />
          </div>
        )}

        {loadError && (
          <div className="font-mono text-xs text-[var(--color-red)]">{loadError}</div>
        )}

        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Experiments" value={String(experiments.length)} />
          <StatCard label="Models" value={String(knownModels.length)} />
          <StatCard label="Average ICS" value={meanIcs} sub="0 = different, 100 = continuous" />
          <StatCard
            label="Perspective consistency"
            value={analysis?.perspective_consistency_score !== null && analysis?.perspective_consistency_score !== undefined
              ? analysis.perspective_consistency_score.toFixed(1)
              : "—"}
            sub={`for ${condition} / ${selectedModel}`}
          />
        </section>

        <section>
          <Panel
            eyebrow="Identity curve"
            title={`ICS vs. transformation — ${condition}`}
            className=""
          >
            <div className="flex flex-wrap gap-2 mb-4 font-mono text-xs">
              {CONDITIONS.map((c) => (
                <button
                  key={c}
                  onClick={() => setCondition(c)}
                  className={`px-3 py-1.5 rounded-sm border ${
                    condition === c
                      ? "border-[var(--color-amber)] text-[var(--color-amber)]"
                      : "border-[var(--color-line)] text-[var(--color-text-dim)] hover:border-[var(--color-line-bright)]"
                  }`}
                >
                  {c}
                </button>
              ))}
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="ml-auto bg-[var(--color-panel-raised)] border border-[var(--color-line)] rounded-sm px-2 py-1 text-[var(--color-text)]"
              >
                {(knownModels.length ? knownModels : ["demo-model"]).map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
            {isDemoSelected && <div className="mb-3"><DemoBadge /></div>}
            <IdentityCurveChart curve={analysis?.curve ?? []} boundary={analysis?.identity_boundary ?? null} />
          </Panel>
        </section>

        <section className="grid md:grid-cols-2 gap-6">
          <ExperimentRunner availableModels={modelsInfo?.models ?? []} onRan={refreshExperiments} />

          <Panel eyebrow="Export" title="Export & report">
            <div className="flex flex-col gap-3 font-mono text-xs">
              <a
                href={api.exportJsonUrl()}
                className="border border-[var(--color-line)] rounded-sm px-3 py-2 hover:border-[var(--color-line-bright)] text-[var(--color-text-dim)]"
              >
                ↓ Export all data as JSON
              </a>
              <a
                href={api.exportCsvUrl()}
                className="border border-[var(--color-line)] rounded-sm px-3 py-2 hover:border-[var(--color-line-bright)] text-[var(--color-text-dim)]"
              >
                ↓ Export all data as CSV
              </a>
              <button
                onClick={async () => {
                  const blob = await api.generateReport();
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = "eidolon_report.md";
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className="border border-[var(--color-line)] rounded-sm px-3 py-2 hover:border-[var(--color-line-bright)] text-left text-[var(--color-text-dim)]"
              >
                ↓ Generate Markdown research report
              </button>
              <p className="text-[var(--color-text-faint)] mt-2 leading-relaxed">
                EIDOLON does not determine whether AI systems are conscious, sentient,
                self-aware, or capable of subjective experience. It evaluates model
                outputs and behavioral consistency regarding digital identity under
                controlled transformations.
              </p>
            </div>
          </Panel>
        </section>

        <section>
          <ResultsTable experiments={experiments} />
        </section>
      </main>
    </div>
  );
}

export default App;
