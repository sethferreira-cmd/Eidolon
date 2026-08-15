import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import system, experiments, analysis, exports
from app.services.demo_data import generate_demo_dataset

app = FastAPI(title="EIDOLON API", description="Evaluating Identity Dynamics in Artificial Entities")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(experiments.router)
app.include_router(analysis.router)
app.include_router(exports.router)


@app.on_event("startup")
def on_startup():
    init_db()
    # Ensure Demo Mode always has data available, even on a fresh DB,
    # so the dashboard is never empty when Ollama isn't installed.
    from app.database import get_conn
    with get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) as c FROM experiments WHERE is_demo=1").fetchone()["c"]
    if count == 0:
        generate_demo_dataset()
