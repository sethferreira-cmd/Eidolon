import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea,
} from "recharts";
import type { CurvePoint, IdentityBoundary } from "../types";

export function IdentityCurveChart({
  curve,
  boundary,
}: {
  curve: CurvePoint[];
  boundary: IdentityBoundary | null;
}) {
  if (!curve.length) {
    return (
      <div className="font-mono text-sm text-[var(--color-text-dim)] py-12 text-center">
        No data for this condition / model yet.
      </div>
    );
  }

  return (
    <div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={curve} margin={{ top: 10, right: 20, bottom: 0, left: -10 }}>
          <CartesianGrid stroke="var(--color-line)" strokeDasharray="2 4" />
          <XAxis
            dataKey="transformation_percentage"
            stroke="var(--color-text-faint)"
            tick={{ fill: "var(--color-text-dim)", fontSize: 11, fontFamily: "var(--font-mono)" }}
            label={{ value: "transformation %", position: "insideBottom", offset: -2, fill: "var(--color-text-faint)", fontSize: 10 }}
          />
          <YAxis
            domain={[0, 100]}
            stroke="var(--color-text-faint)"
            tick={{ fill: "var(--color-text-dim)", fontSize: 11, fontFamily: "var(--font-mono)" }}
            label={{ value: "ICS", angle: -90, position: "insideLeft", fill: "var(--color-text-faint)", fontSize: 10 }}
          />
          <Tooltip
            contentStyle={{
              background: "var(--color-panel-raised)",
              border: "1px solid var(--color-line)",
              borderRadius: 2,
              fontFamily: "var(--font-mono)",
              fontSize: 12,
            }}
            labelFormatter={(v) => `transformation: ${v}%`}
            formatter={(v) => [typeof v === "number" ? v.toFixed(1) : String(v ?? ""), "ICS"]}
          />
          {boundary?.has_sufficient_data && boundary.identity_boundary_from_pct !== undefined && (
            <ReferenceArea
              x1={boundary.identity_boundary_from_pct}
              x2={boundary.identity_boundary_to_pct}
              fill={boundary.phase_transition_detected ? "var(--color-red)" : "var(--color-amber)"}
              fillOpacity={0.12}
              strokeOpacity={0}
            />
          )}
          <Line
            type="monotone"
            dataKey="ics"
            stroke="var(--color-amber)"
            strokeWidth={2}
            dot={{ r: 3, fill: "var(--color-amber)", strokeWidth: 0 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
      {boundary && (
        <div className="mt-3 font-mono text-xs text-[var(--color-text-dim)] border-t border-[var(--color-line)] pt-3">
          {boundary.has_sufficient_data ? (
            <>
              <span className={boundary.phase_transition_detected ? "text-[var(--color-red)]" : "text-[var(--color-amber)]"}>
                {boundary.message}
              </span>
              {boundary.identity_boundary_drop !== undefined && (
                <span className="text-[var(--color-text-faint)]">
                  {" "}— largest drop: {boundary.identity_boundary_drop.toFixed(1)} pts between{" "}
                  {boundary.identity_boundary_from_pct}% and {boundary.identity_boundary_to_pct}%
                </span>
              )}
            </>
          ) : (
            boundary.message
          )}
        </div>
      )}
    </div>
  );
}
