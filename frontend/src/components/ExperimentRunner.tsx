import { useState } from "react";
import { api } from "../services/api";
import type { Condition, RunResult } from "../types";
import { Panel } from "./Panel";

const CONDITIONS: Condition[] = ["memory", "personality", "values", "goals", "model", "progressive"];
const QUESTIONS_PER_TRIAL = 5;

export function ExperimentRunner({
  availableModels,
  onRan,
}: {
  availableModels: string[];
  onRan: () => void;
}) {
  const [model, setModel] = useState<string>(availableModels[0] || "demo");
  const [condition, setCondition] = useState<Condition>("memory");
  const [pct, setPct] = useState(50);
  const [trials, setTrials] = useState(5);
  const [blind, setBlind] = useState(false);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const estimatedCalls = trials * QUESTIONS_PER_TRIAL;

  async function handleRun() {
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.runExperiment({
        model,
        condition,
        transformation_percentage: pct,
        trial_count: trials,
        blind_condition: blind,
      });
      setResult(res);
      onRan();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Run failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <Panel eyebrow="Experiment runner" title="Run an experiment">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 font-mono text-xs">
        <label className="flex flex-col gap-1">
          <span className="text-[var(--color-text-faint)] uppercase tracking-widest text-[10px]">Model</span>
          <select
            className="bg-[var(--color-panel-raised)] border border-[var(--color-line)] rounded-sm px-2 py-1.5 text-[var(--color-text)]"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="demo">demo (regenerate synthetic data)</option>
            {availableModels.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-[var(--color-text-faint)] uppercase tracking-widest text-[10px]">Condition</span>
          <select
            className="bg-[var(--color-panel-raised)] border border-[var(--color-line)] rounded-sm px-2 py-1.5 text-[var(--color-text)]"
            value={condition}
            onChange={(e) => setCondition(e.target.value as Condition)}
          >
            {CONDITIONS.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-[var(--color-text-faint)] uppercase tracking-widest text-[10px]">
            Transformation: {pct}%
          </span>
          <input
            type="range"
            min={0}
            max={100}
            step={10}
            value={pct}
            onChange={(e) => setPct(Number(e.target.value))}
            className="accent-[var(--color-amber)]"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-[var(--color-text-faint)] uppercase tracking-widest text-[10px]">Trials</span>
          <select
            className="bg-[var(--color-panel-raised)] border border-[var(--color-line)] rounded-sm px-2 py-1.5 text-[var(--color-text)]"
            value={trials}
            onChange={(e) => setTrials(Number(e.target.value))}
          >
            {[5, 10, 20, 50].map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </label>

        <label className="flex items-center gap-2 mt-5">
          <input type="checkbox" checked={blind} onChange={(e) => setBlind(e.target.checked)} className="accent-[var(--color-amber)]" />
          <span className="text-[var(--color-text-dim)]">Blind condition (System A / B)</span>
        </label>
      </div>

      {model !== "demo" && (
        <div className="mt-4 font-mono text-[11px] text-[var(--color-text-faint)] border-t border-[var(--color-line)] pt-3">
          Estimated computation: {estimatedCalls <= 25 ? "Low" : estimatedCalls <= 100 ? "Medium" : "High"} —{" "}
          {trials} trials × {QUESTIONS_PER_TRIAL} questions = {estimatedCalls} local inference calls. Runs locally
          through Ollama; CPU/RAM usage may increase.
        </div>
      )}

      <button
        onClick={handleRun}
        disabled={running}
        className="mt-4 font-mono text-xs uppercase tracking-widest bg-[var(--color-amber)] text-[var(--color-ink)] px-4 py-2 rounded-sm disabled:opacity-50 hover:brightness-110 transition"
      >
        {running ? "Running…" : "Run experiment"}
      </button>

      {error && (
        <div className="mt-3 font-mono text-xs text-[var(--color-red)] border border-[var(--color-red)]/40 rounded-sm px-3 py-2">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-3 font-mono text-xs text-[var(--color-text-dim)] border border-[var(--color-line)] rounded-sm px-3 py-2">
          status: <span className="text-[var(--color-cyan)]">{result.status}</span>
          {result.results && (
            <span>
              {" "}— {result.results.filter((r) => r.ok).length}/{result.results.length} calls succeeded
            </span>
          )}
        </div>
      )}
    </Panel>
  );
}
