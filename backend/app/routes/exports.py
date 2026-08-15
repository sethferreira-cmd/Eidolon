import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.database import get_conn, row_to_dict

router = APIRouter()


def _all_rows():
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT e.id as experiment_id, e.condition, e.transformation_percentage, e.model,
                      e.blind_condition, e.is_demo, r.trial_index, r.question_id, r.perspective,
                      s.same_entity, s.identity_score, s.confidence, s.primary_identity_property, s.reason
               FROM experiments e
               JOIN runs r ON r.experiment_id = e.id
               LEFT JOIN scores s ON s.run_id = r.id
               ORDER BY e.created_at"""
        ).fetchall()
        return [row_to_dict(r) for r in rows]


@router.get("/export/json")
def export_json():
    rows = _all_rows()
    buf = io.BytesIO(json.dumps(rows, indent=2, default=str).encode("utf-8"))
    return StreamingResponse(
        buf, media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=eidolon_export.json"},
    )


@router.get("/export/csv")
def export_csv():
    rows = _all_rows()
    buf = io.StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    out = io.BytesIO(buf.getvalue().encode("utf-8"))
    return StreamingResponse(
        out, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=eidolon_export.csv"},
    )


@router.post("/reports/generate")
def generate_report():
    with get_conn() as conn:
        exps = conn.execute("SELECT * FROM experiments").fetchall()

    lines = []
    lines.append("# EIDOLON Research Report\n")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z\n")
    lines.append("## Abstract\n")
    lines.append(
        "This report summarizes EIDOLON experiment data on identity continuity "
        "judgements under controlled transformations of memory, personality, "
        "values, goals, and underlying model. Observations are separated from "
        "interpretation below.\n"
    )
    lines.append("## Research Question\n")
    lines.append("When does an AI stop being itself?\n")
    lines.append("## Scientific Safety Statement\n")
    lines.append(
        "EIDOLON does not determine whether AI systems are conscious, sentient, "
        "self-aware, or capable of subjective experience. It evaluates model "
        "outputs and behavioral consistency regarding digital identity under "
        "controlled transformations.\n"
    )
    lines.append("## Experiments Recorded\n")
    lines.append(f"Total experiments: {len(exps)}\n")

    real = [e for e in exps if not e["is_demo"]]
    demo = [e for e in exps if e["is_demo"]]
    lines.append(f"- Real (Ollama-backed): {len(real)}\n")
    lines.append(f"- Demo (synthetic, NOT research data): {len(demo)}\n")

    lines.append("## Observations\n")
    for e in real:
        d = row_to_dict(e)
        lines.append(f"- {d['id']}: condition={d['condition']}, transformation={d['transformation_percentage']}%, model={d['model']}, status={d['status']}\n")
    if not real:
        lines.append("- No real experiments have been run yet. Run experiments via Ollama to populate this section.\n")

    lines.append("## Interpretation\n")
    lines.append(
        "Interpretation is intentionally left to the researcher reviewing this "
        "report. This generator does not draw conclusions beyond what is "
        "directly observed in the Observations section above.\n"
    )
    lines.append("## Limitations\n")
    lines.append(
        "- Small local models may produce inconsistent JSON formatting, reducing usable sample size.\n"
        "- Identity scores are self-reports from the model under study, not ground truth.\n"
        "- Demo data is entirely synthetic and must not be cited as a finding.\n"
    )
    lines.append("## Reproducibility\n")
    lines.append("Each experiment stores its random_seed, prompt_version, model, and trial_count for exact reproduction.\n")

    report_text = "\n".join(lines)
    buf = io.BytesIO(report_text.encode("utf-8"))
    return StreamingResponse(
        buf, media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=eidolon_report.md"},
    )
