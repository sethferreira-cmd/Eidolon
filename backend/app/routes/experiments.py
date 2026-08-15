from fastapi import APIRouter, HTTPException

from app.database import get_conn, row_to_dict
from app.schemas import ExperimentRunRequest
from app.services.experiment_engine import run_experiment
from app.services.demo_data import generate_demo_dataset, DEMO_MODEL_NAME

router = APIRouter()


@router.get("/experiments")
def list_experiments():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM experiments ORDER BY created_at DESC").fetchall()
        out = []
        for r in rows:
            d = row_to_dict(r)
            agg = conn.execute(
                "SELECT AVG(identity_score) as mean_ics, AVG(confidence) as mean_conf FROM scores WHERE experiment_id=?",
                (d["id"],),
            ).fetchone()
            d["identity_score_mean"] = agg["mean_ics"]
            d["confidence_mean"] = agg["mean_conf"]
            out.append(d)
        return out


@router.get("/experiments/{experiment_id}")
def get_experiment(experiment_id: str):
    with get_conn() as conn:
        exp = conn.execute("SELECT * FROM experiments WHERE id=?", (experiment_id,)).fetchone()
        if not exp:
            raise HTTPException(status_code=404, detail="Experiment not found")
        runs = conn.execute("SELECT * FROM runs WHERE experiment_id=?", (experiment_id,)).fetchall()
        run_list = []
        for r in runs:
            rd = row_to_dict(r)
            resp = conn.execute("SELECT * FROM responses WHERE run_id=?", (rd["id"],)).fetchone()
            score = conn.execute("SELECT * FROM scores WHERE run_id=?", (rd["id"],)).fetchone()
            rd["response"] = row_to_dict(resp) if resp else None
            rd["score"] = row_to_dict(score) if score else None
            run_list.append(rd)
        return {"experiment": row_to_dict(exp), "runs": run_list}


@router.post("/experiments/run")
def run(req: ExperimentRunRequest):
    if req.condition not in ("memory", "personality", "values", "goals", "model", "progressive"):
        raise HTTPException(status_code=400, detail=f"Invalid condition: {req.condition}")

    if req.model == "demo":
        generate_demo_dataset()
        return {"status": "demo_regenerated", "model": DEMO_MODEL_NAME}

    estimated_calls = req.trial_count * 5  # 5 questions in the default bank
    result = run_experiment(
        model=req.model,
        condition=req.condition,
        transformation_percentage=req.transformation_percentage,
        trial_count=req.trial_count,
        blind_condition=req.blind_condition,
        random_seed=req.random_seed or 42,
        question_ids=req.question_set,
    )
    result["estimated_calls"] = estimated_calls
    return result
