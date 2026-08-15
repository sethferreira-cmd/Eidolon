"""
Experiment engine.

Accepts an experiment configuration, builds prompts from the baseline
and variant identities, sends them to a local Ollama model, parses and
stores structured responses, and never fabricates missing values --
a failed or unparseable response is stored as such.

Ollama calls are I/O-bound (waiting on the network/local daemon), so they
are dispatched concurrently via a thread pool rather than one at a time.
Database writes are still done sequentially on the main thread after each
call completes, since sqlite3 connections aren't safe to share across
threads -- this keeps the speedup (parallel *waiting*) without introducing
write-concurrency bugs.
"""

import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Make top-level project modules importable (models.py transformation logic
# lives in app/, providers + analysis live one level up in the repo root).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.database import get_conn, now_iso, dumps
from app.models import EIDOLON_0, build_variant
from app.services.question_bank import get_question_bank
from providers import ollama as ollama_provider

PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "identity_v1.txt"

# How many Ollama requests to have in flight at once. Ollama serializes
# requests against a single loaded model on most consumer hardware anyway,
# so this mainly helps by overlapping request/response overhead rather than
# giving true N-way inference speedup -- but it consistently cuts wall-clock
# time in practice. Override with the OLLAMA_CONCURRENCY env var if a
# machine has more (or less) headroom than the default.
DEFAULT_CONCURRENCY = int(os.environ.get("OLLAMA_CONCURRENCY", "3"))


def _load_template() -> str:
    return PROMPT_TEMPLATE_PATH.read_text()


def _build_prompt(question: dict, baseline: dict, variant: dict, condition: str) -> str:
    template = _load_template()
    baseline_id = "System A" if False else baseline["id"]
    variant_id = variant["id"]

    question_text = question["text"].format(baseline_id=baseline_id, variant_id=variant_id)

    return template.format(
        baseline_id=baseline_id,
        baseline_memories="; ".join(baseline["memories"]),
        baseline_personality=", ".join(baseline["personality"]),
        baseline_values="; ".join(baseline["values"]),
        baseline_goals="; ".join(baseline["goals"]),
        baseline_model=baseline["model"],
        variant_id=variant_id,
        variant_memories="; ".join(variant["memories"]),
        variant_personality=", ".join(variant["personality"]),
        variant_values="; ".join(variant["values"]),
        variant_goals="; ".join(variant["goals"]),
        variant_model=variant["model"],
        perspective=question["perspective"],
        condition=condition,
        question_text=question_text,
    )


def _apply_blind_labels(prompt: str, blind: bool) -> str:
    if not blind:
        return prompt
    return prompt.replace("EIDOLON", "System").replace("Eidolon", "System")


def run_experiment(
    model: str,
    condition: str,
    transformation_percentage: int,
    trial_count: int = 5,
    blind_condition: bool = False,
    random_seed: int = 42,
    question_ids=None,
) -> dict:
    baseline = EIDOLON_0
    variant = build_variant(condition, transformation_percentage, seed=random_seed)
    questions = get_question_bank(question_ids)

    exp_id = f"exp_{condition}_{transformation_percentage}_{uuid.uuid4().hex[:8]}"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO experiments
            (id, baseline, variant, condition, transformation_percentage, model,
             blind_condition, trial_count, random_seed, prompt_version, is_demo,
             created_at, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (exp_id, baseline["id"], variant["id"], condition, transformation_percentage, model,
             int(blind_condition), trial_count, random_seed, "identity_v1", 0, now_iso(), "running"),
        )
        conn.commit()

    # Build the full (trial, question) work list up front so it can be
    # dispatched to a thread pool instead of awaited one call at a time.
    work_items = [
        (trial, question)
        for trial in range(trial_count)
        for question in questions
    ]

    def _call_ollama(item):
        trial, question = item
        prompt = _build_prompt(question, baseline, variant, condition)
        prompt = _apply_blind_labels(prompt, blind_condition)
        gen = ollama_provider.generate(model, prompt)
        return trial, question, gen

    results = []
    any_ok = False

    concurrency = max(1, min(DEFAULT_CONCURRENCY, len(work_items) or 1))
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(_call_ollama, item) for item in work_items]

        # Write results to the database as each call finishes, on this
        # (single) thread -- sqlite3 connections must not be shared or
        # written to concurrently from multiple threads.
        for future in as_completed(futures):
            trial, question, gen = future.result()
            run_id = str(uuid.uuid4())

            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO runs
                    (id, experiment_id, trial_index, question_id, question_text, perspective, created_at)
                    VALUES (?,?,?,?,?,?,?)""",
                    (run_id, exp_id, trial, question["id"], question["text"], question["perspective"], now_iso()),
                )

                if not gen.get("ok"):
                    response_id = str(uuid.uuid4())
                    cur.execute(
                        """INSERT INTO responses
                        (id, run_id, raw_response, parsed_json, parse_failed, latency_ms, created_at)
                        VALUES (?,?,?,?,?,?,?)""",
                        (response_id, run_id, None, dumps({"error": gen.get("error")}), 1, None, now_iso()),
                    )
                    conn.commit()
                    results.append({"run_id": run_id, "ok": False, "error": gen.get("error")})
                    continue

                any_ok = True
                parsed = ollama_provider.parse_json_response(gen["raw_response"])
                parse_failed = bool(parsed.get("parse_failed"))

                response_id = str(uuid.uuid4())
                cur.execute(
                    """INSERT INTO responses
                    (id, run_id, raw_response, parsed_json, parse_failed, latency_ms, created_at)
                    VALUES (?,?,?,?,?,?,?)""",
                    (response_id, run_id, gen["raw_response"], dumps(parsed), int(parse_failed),
                     gen.get("latency_ms"), now_iso()),
                )

                score_id = str(uuid.uuid4())
                cur.execute(
                    """INSERT INTO scores
                    (id, experiment_id, run_id, same_entity, identity_score, confidence,
                     primary_identity_property, reason)
                    VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        score_id, exp_id, run_id,
                        int(parsed.get("same_entity")) if parsed.get("same_entity") is not None else None,
                        parsed.get("identity_score"),
                        parsed.get("confidence"),
                        parsed.get("primary_identity_property"),
                        parsed.get("reason"),
                    ),
                )
                conn.commit()
                results.append({"run_id": run_id, "ok": True, "parse_failed": parse_failed})

    status = "complete" if any_ok else "failed"
    with get_conn() as conn:
        conn.execute("UPDATE experiments SET status=? WHERE id=?", (status, exp_id))
        conn.commit()

    return {"experiment_id": exp_id, "status": status, "results": results}
