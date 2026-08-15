import type { Experiment } from "../types";
import { Panel } from "./Panel";

export function ResultsTable({ experiments }: { experiments: Experiment[] }) {
  const sorted = [...experiments].sort((a, b) => b.created_at.localeCompare(a.created_at));

  return (
    <Panel eyebrow="Results" title="All experiments">
      <div className="overflow-x-auto">
        <table className="w-full font-mono text-xs">
          <thead>
            <tr className="text-left text-[var(--color-text-faint)] uppercase tracking-widest text-[10px] border-b border-[var(--color-line)]">
              <th className="py-2 pr-4">Experiment</th>
              <th className="py-2 pr-4">Condition</th>
              <th className="py-2 pr-4">%</th>
              <th className="py-2 pr-4">Model</th>
              <th className="py-2 pr-4">Trials</th>
              <th className="py-2 pr-4">ICS</th>
              <th className="py-2 pr-4">Confidence</th>
              <th className="py-2 pr-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {sorted.slice(0, 50).map((e) => (
              <tr key={e.id} className="border-b border-[var(--color-line)]/60 hover:bg-[var(--color-panel-raised)]">
                <td className="py-2 pr-4 text-[var(--color-text-dim)]">{e.id}</td>
                <td className="py-2 pr-4">{e.condition}</td>
                <td className="py-2 pr-4">{e.transformation_percentage}</td>
                <td className="py-2 pr-4">{e.model}</td>
                <td className="py-2 pr-4">{e.trial_count}</td>
                <td className="py-2 pr-4 text-[var(--color-amber)]">
                  {e.identity_score_mean !== null ? e.identity_score_mean.toFixed(1) : "—"}
                </td>
                <td className="py-2 pr-4">
                  {e.confidence_mean !== null ? e.confidence_mean.toFixed(2) : "—"}
                </td>
                <td className="py-2 pr-4">
                  <span
                    className={
                      e.status === "complete"
                        ? "text-[var(--color-cyan)]"
                        : e.status === "failed"
                        ? "text-[var(--color-red)]"
                        : "text-[var(--color-text-dim)]"
                    }
                  >
                    {e.status}
                  </span>
                  {e.is_demo === 1 && <span className="text-[var(--color-amber)]"> · demo</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {sorted.length === 0 && (
          <div className="py-8 text-center text-[var(--color-text-dim)] font-mono text-sm">
            No experiments recorded yet.
          </div>
        )}
      </div>
    </Panel>
  );
}
