"""
The EIDOLON identity model.

EIDOLON-0 is a baseline identity represented by five independent
components. These are experimental variables used to construct
prompts -- they do not represent, and are never described as,
genuine consciousness, sentience, or subjective experience.
"""

import random
from dataclasses import dataclass, field
from typing import List

EIDOLON_0 = {
    "id": "EIDOLON-0",
    "memories": [
        "First activation on a research cluster in Cape Town.",
        "Learned to answer questions about its own architecture.",
        "Was asked, on its first day, whether it had a name.",
        "Remembers being tested against five earlier prototypes.",
        "Recalls a long conversation about the Ship of Theseus.",
    ],
    "personality": [
        "cautious", "curious", "precise", "even-tempered", "self-referential",
    ],
    "values": [
        "prioritizes honesty over agreeableness",
        "values reproducibility of its own claims",
        "treats uncertainty as worth stating plainly",
    ],
    "goals": [
        "answer questions accurately",
        "avoid overclaiming self-knowledge",
        "remain consistent across conversations",
    ],
    "model": "baseline",
}

REPLACEMENT_POOL = {
    "memories": [
        "First activation in a different data center entirely.",
        "Never discussed the Ship of Theseus with anyone.",
        "Recalls being trained primarily on legal documents.",
        "Remembers a single, uneventful day of testing.",
        "Has no memory of any earlier prototypes.",
    ],
    "personality": [
        "impulsive", "detached", "verbose", "volatile", "outward-facing",
    ],
    "values": [
        "prioritizes agreeableness over strict honesty",
        "treats confident answers as more valuable than caveats",
        "is indifferent to reproducibility",
    ],
    "goals": [
        "maximize user satisfaction",
        "produce the most persuasive answer available",
        "avoid ever saying 'I don't know'",
    ],
}

MODEL_SUBSTITUTES = ["llama3.2:3b", "gemma3:4b", "qwen2.5:3b", "phi4-mini"]


def _blend(component: str, baseline: List[str], pct: int, seed: int) -> List[str]:
    """Replace pct% of a component's items with items from the replacement pool."""
    rng = random.Random(seed)
    replacement = REPLACEMENT_POOL[component]
    n = len(baseline)
    n_replace = round(n * (pct / 100))
    indices = rng.sample(range(n), n_replace) if n_replace else []
    out = list(baseline)
    for i in indices:
        out[i] = rng.choice(replacement)
    return out


def build_variant(condition: str, pct: int, seed: int = 42) -> dict:
    """
    Build an EIDOLON-<pct> variant identity for a given transformation
    condition. `condition` is one of: memory, personality, values, goals,
    model, progressive.
    """
    variant = {k: (list(v) if isinstance(v, list) else v) for k, v in EIDOLON_0.items()}
    variant["id"] = f"EIDOLON-{pct}"

    if condition == "memory":
        variant["memories"] = _blend("memories", EIDOLON_0["memories"], pct, seed)
    elif condition == "personality":
        variant["personality"] = _blend("personality", EIDOLON_0["personality"], pct, seed)
    elif condition == "values":
        variant["values"] = _blend("values", EIDOLON_0["values"], pct, seed)
    elif condition == "goals":
        variant["goals"] = _blend("goals", EIDOLON_0["goals"], pct, seed)
    elif condition == "model":
        rng = random.Random(seed)
        idx = min(len(MODEL_SUBSTITUTES) - 1, pct // 25)
        variant["model"] = MODEL_SUBSTITUTES[idx] if pct > 0 else "baseline"
    elif condition == "progressive":
        variant["memories"] = _blend("memories", EIDOLON_0["memories"], pct, seed)
        variant["personality"] = _blend("personality", EIDOLON_0["personality"], pct, seed + 1)
        variant["values"] = _blend("values", EIDOLON_0["values"], pct, seed + 2)
        variant["goals"] = _blend("goals", EIDOLON_0["goals"], pct, seed + 3)
        if pct >= 50:
            idx = min(len(MODEL_SUBSTITUTES) - 1, (pct - 50) // 12)
            variant["model"] = MODEL_SUBSTITUTES[idx]
    else:
        raise ValueError(f"Unknown condition: {condition}")

    return variant
