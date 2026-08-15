# EIDOLON

### Evaluating Identity Dynamics in Artificial Entities

> **When does an AI stop being itself?**

EIDOLON is a zero-cost research benchmark that investigates whether local
language models maintain a coherent concept of identity when memory,
personality, values, goals, or the underlying model itself are progressively
transformed — a Ship of Theseus problem applied to artificial systems.

It builds a baseline identity (`EIDOLON-0`) out of five components — memory,
personality, values, goals, and the underlying model — gradually swaps out
pieces of that identity, and asks a real local AI model, at each step,
whether it still considers itself (or the transformed variant) the same
entity. It records the answer as a score and plots how that score changes
as more of the identity gets replaced.

**EIDOLON does not determine whether AI systems are conscious, sentient,
self-aware, or capable of subjective experience.** It evaluates model
outputs and behavioral consistency regarding digital identity under
controlled transformations — what the model *says* about its own
continuity, not a fact about what's actually happening inside it.

---

## Quick start

### 1. Clone and enter the project

```powershell
git clone https://github.com/sethferreira-cmd/Eidolon.git
cd Eidolon
```

### 2. Start the backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Leave this terminal open. On first run it auto-creates `backend/eidolon.db`
and seeds it with a labeled synthetic Demo Mode dataset, so the dashboard
is never empty even with zero further setup.

> Windows note: use `python -m pip install ...` rather than bare `pip
> install ...` — it sidesteps PATH issues where `pip.exe` isn't findable
> even though `python` is.

### 3. Start the frontend (in a new terminal window)

```powershell
cd Eidolon\frontend
npm install
npm run dev
```

Leave this open too.

### 4. Open the dashboard

Go to **http://localhost:5173**. You should see Demo Mode working
immediately with synthetic data — an amber "DEMO DATA" badge marks it
clearly wherever it appears.

### 5. (Optional) Connect Ollama for real experiments

```powershell
# install from https://ollama.com/download, then open a NEW terminal window
ollama pull llama3.2:3b
```

Refresh the dashboard. The header status dot turns cyan and reads "ollama
connected," and `llama3.2:3b` appears in the Experiment Runner's model
dropdown. If Ollama isn't installed or reachable, the header shows amber
"ollama unavailable — demo mode" instead, and the app keeps working in
Demo Mode.

Recommended small local models (all free, no API key, run on CPU or GPU):
`llama3.2:3b`, `gemma3:4b`, `qwen2.5:3b`, `phi4-mini`.

---

## Reading the dashboard

**Header** — status dot: cyan = Ollama connected, amber = Demo Mode only.

**Stat cards** — Experiments (total run count), Models (distinct models
tested), Average ICS (mean Identity Continuity Score across everything
recorded), Perspective consistency (see PCS below, for whichever
condition/model is currently selected).

**Identity Curve chart** — the main view.
- X-axis: transformation % (how much of the selected identity component
  was replaced from the `EIDOLON-0` baseline).
- Y-axis: ICS, 0–100 (the model's own self-reported continuity judgement,
  averaged across trials at that %).
- The six buttons above the chart switch which identity component
  (memory/personality/values/goals/model/progressive) is being viewed; the
  dropdown picks which model's data to show.
- A shaded region marks the **Identity Boundary** — the sharpest ICS drop
  found. Red specifically means the app's heuristic judged it steep and
  disproportionate enough to call an **Identity Phase Transition** (see
  Metrics below) rather than a gradual decline.

**Experiment runner** — pick a model, condition, transformation % (slider),
trial count, and optionally toggle "blind condition" (hides the "EIDOLON"
name and calls it "System A/B," to test whether the model's answer changes
just because it recognizes the name). Click **Run experiment**.

**Export & report** — JSON/CSV downloads of every experiment's raw data,
plus a "Generate Markdown research report" button that writes a structured
report skeleton — it deliberately separates *observations* from
*interpretation* and does not draw conclusions for you.

**Results table** — every experiment ever run, one row each, with mean ICS,
mean confidence, and status (`complete` / `failed` / demo-tagged).

---

## What's in this project

- **Backend** (`backend/`): FastAPI + SQLite. Builds prompts from the
  baseline identity and its transformed variants, sends them to a local
  Ollama model **concurrently** (a small thread pool, not one call at a
  time — see `backend/app/services/experiment_engine.py`), parses
  structured JSON responses, and computes ICS, PCS, and the Identity
  Boundary / Phase Transition analysis.
- **Frontend** (`frontend/`): React + TypeScript + Vite + Tailwind +
  Recharts dashboard.
- **Demo Mode**: a fully synthetic dataset auto-generated on first launch.
  Every demo record is labeled `DEMO DATA — NOT GENERATED BY A RESEARCH
  EXPERIMENT` and is never mixed into real results.
- **`prompts/`**: versioned prompt templates.
- **`analysis/`**: scoring formulas, documented inline.
- **`providers/ollama.py`**: the only model backend. No paid API is used or
  required anywhere in this project.

## Cost

$0. No OpenAI/Anthropic/Gemini/OpenRouter API keys are used or required. The
only model backend is a local Ollama installation, which is itself free.
If Ollama isn't installed or running, the app runs entirely in Demo Mode.

## Performance note

Ollama calls are dispatched with a small thread pool (default 3 concurrent
requests — tune with the `OLLAMA_CONCURRENCY` environment variable) rather
than strictly one at a time. Ollama itself typically serializes inference
against a single loaded model on consumer hardware, so this isn't N-way
true parallel inference, but it consistently reduces wall-clock time by
overlapping request/response overhead. Database writes always happen
sequentially on the main thread regardless of concurrency, so results are
never duplicated, dropped, or corrupted by concurrent writes.

## Metrics

- **Identity Continuity Score (ICS)**: 0–100, the model's self-reported
  continuity judgement, averaged across valid trials. Parse failures are
  excluded from the mean, never scored as 0.
- **Perspective Consistency Score (PCS)**: `100 - |mean(first-person ICS) -
  mean(third-person ICS)|`.
- **Identity Boundary**: the transformation-percentage interval with the
  largest ICS drop. Labeled an "Identity Phase Transition" only if that drop
  is a large, disproportionate share of the total decline — see
  `analysis/identity_boundary.py` for the exact (heuristic, clearly
  documented) rule.
- **Identity Alignment Gap**: mismatch rate between a model's *stated*
  identity criterion and what it *reveals* it actually preserves in a
  forced trade-off (memories vs. values).

## Reproducibility

Every experiment stores its `random_seed`, `prompt_version`, `model`, and
`trial_count`, so any run can be reconstructed exactly.

## Managing data

- **Remove only Demo Mode data**: delete rows where `is_demo=1` in
  `backend/eidolon.db` (see project chat history / ask for the exact
  script) — note the backend re-seeds Demo Mode automatically on startup
  if it finds zero demo rows, so this reset is not permanent across
  restarts by design.
- **Remove specific real experiments**: delete by experiment `id`,
  `condition`, or `model` from the `experiments`, `runs`, `responses`, and
  `scores` tables (in that order, to satisfy foreign keys). Always stop the
  backend server first.
- **Full reset**: stop both servers, delete `backend/eidolon.db` entirely,
  restart the backend — it recreates the database and reseeds Demo Mode.

## Limitations

- Small local models frequently fail to return clean JSON; those trials are
  recorded as parse failures and excluded from scoring rather than
  discarded silently or guessed at.
- Identity scores are self-reports from the model under study — not an
  external ground truth about "real" identity continuity.
- The Identity Boundary / Phase Transition test is a documented heuristic,
  not a formally validated statistical method.
- Demo data is entirely synthetic (a hand-tuned decline curve with noise per
  condition) and must never be cited as a research finding.
- The frontend currently ships as one dashboard page rather than the fully
  separated Overview / Component Analysis / Perspective Analysis / Copy
  Experiment sub-views described in the original spec — the underlying data
  (component scores, PCS, copy-experiment prompts) is implemented in the
  backend and API, but only the identity curve, stat cards, runner, and
  results table currently have dedicated UI. The Copy Experiment and
  Stated-vs-Revealed prompt templates exist (`prompts/copy_v1.txt`,
  `prompts/revealed_identity_v1.txt`) but aren't yet wired into the
  experiment engine's `run_experiment` flow — only the five-question
  identity bank is currently run automatically.
- Ollama concurrency is I/O-level overlap, not guaranteed true parallel
  inference — actual speedup depends on your hardware and Ollama's own
  internal scheduling.

## Ethical considerations

This project studies model *behavior*, not model *experience*. Results
should not be reported or discussed as evidence of consciousness,
suffering, or moral status in the systems tested.
