import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from fastapi import APIRouter, Query

from app.database import get_conn, row_to_dict
from analysis.identity_boundary import analyze_boundary
from analysis.scoring import compute_pcs

router = APIRouter()


@router.get("/results")
def results(condition: str = Query(None), model: str = Query(None)):
    with get_conn() as conn:
        q = "SELECT * FROM experiments WHERE 1=1"
        params = []
        if condition:
            q += " AND condition=?"
            params.append(condition)
        if model:
            q += " AND model=?"
            params.append(model)
        exps = conn.execute(q, params).fetchall()

        out = []
        for exp in exps:
            d = row_to_dict(exp)
            agg = conn.execute(
                "SELECT AVG(identity_score) as mean_ics FROM scores WHERE experiment_id=?",
                (d["id"],),
            ).fetchone()
            d["ics"] = agg["mean_ics"]
            out.append(d)
        return out


@router.get("/analysis")
def analysis(condition: str = Query(...), model: str = Query(...)):
    with get_conn() as conn:
        exps = conn.execute(
            "SELECT * FROM experiments WHERE condition=? AND model=?",
            (condition, model),
        ).fetchall()

        points = []
        fp_scores, tp_scores = [], []
        for exp in exps:
            d = row_to_dict(exp)
            agg = conn.execute(
                "SELECT AVG(identity_score) as ics FROM scores WHERE experiment_id=?",
                (d["id"],),
            ).fetchone()
            if agg["ics"] is not None:
                points.append({"transformation_percentage": d["transformation_percentage"], "ics": agg["ics"]})

            fp = conn.execute(
                """SELECT s.identity_score FROM scores s
                   JOIN runs r ON s.run_id = r.id
                   WHERE s.experiment_id=? AND r.perspective='first_person'""",
                (d["id"],),
            ).fetchall()
            tp = conn.execute(
                """SELECT s.identity_score FROM scores s
                   JOIN runs r ON s.run_id = r.id
                   WHERE s.experiment_id=? AND r.perspective='third_person'""",
                (d["id"],),
            ).fetchall()
            fp_scores += [row["identity_score"] for row in fp if row["identity_score"] is not None]
            tp_scores += [row["identity_score"] for row in tp if row["identity_score"] is not None]

        boundary = analyze_boundary(points)
        pcs = compute_pcs(fp_scores, tp_scores)

        return {
            "condition": condition,
            "model": model,
            "curve": sorted(points, key=lambda p: p["transformation_percentage"]),
            "identity_boundary": boundary,
            "perspective_consistency_score": pcs,
        }
