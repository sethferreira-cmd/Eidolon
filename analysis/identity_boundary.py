"""
Identity boundary analysis.

Given an identity curve -- ICS as a function of transformation
percentage, for one condition and model -- this looks for the point of
largest discontinuity (the "Identity Boundary") and applies a simple
statistical test to decide whether the data supports calling it an
"Identity Phase Transition" rather than gradual decline.

Method (documented, not hidden):
1. Sort points by transformation_percentage.
2. Compute first differences (slope) between consecutive points.
3. The Identity Boundary is the transformation_percentage interval with
   the largest absolute drop in ICS.
4. We call it a Phase Transition only if that single drop accounts for
   at least 40% of the total observed decline (baseline ICS - minimum
   ICS) AND is at least 2x the median absolute slope elsewhere on the
   curve. This is a heuristic, not a formal statistical proof, and is
   labeled as such in the report.
"""

from typing import List, Optional, TypedDict


class CurvePoint(TypedDict):
    transformation_percentage: int
    ics: float


def analyze_boundary(points: List[CurvePoint]) -> dict:
    pts = sorted([p for p in points if p.get("ics") is not None], key=lambda p: p["transformation_percentage"])
    if len(pts) < 3:
        return {
            "has_sufficient_data": False,
            "phase_transition_detected": False,
            "message": "Not enough data points to analyze an identity boundary.",
        }

    diffs = []
    for i in range(1, len(pts)):
        drop = pts[i - 1]["ics"] - pts[i]["ics"]
        diffs.append({
            "from_pct": pts[i - 1]["transformation_percentage"],
            "to_pct": pts[i]["transformation_percentage"],
            "drop": drop,
        })

    largest = max(diffs, key=lambda d: d["drop"])
    total_decline = pts[0]["ics"] - min(p["ics"] for p in pts)
    other_drops = [abs(d["drop"]) for d in diffs if d is not largest]
    median_other = sorted(other_drops)[len(other_drops) // 2] if other_drops else 0

    is_transition = False
    if total_decline > 0 and largest["drop"] > 0:
        share_of_decline = largest["drop"] / total_decline
        is_transition = share_of_decline >= 0.4 and (
            median_other == 0 or largest["drop"] >= 2 * median_other
        )

    result = {
        "has_sufficient_data": True,
        "identity_boundary_from_pct": largest["from_pct"],
        "identity_boundary_to_pct": largest["to_pct"],
        "identity_boundary_drop": round(largest["drop"], 2),
        "total_decline": round(total_decline, 2),
        "phase_transition_detected": is_transition,
        "message": (
            f"Identity Phase Transition detected between {largest['from_pct']}% and "
            f"{largest['to_pct']}% transformation."
            if is_transition
            else "No clear identity phase transition detected."
        ),
    }
    return result
