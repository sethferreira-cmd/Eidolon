"""
Versioned identity question bank (v1).

Each question has an id, category, perspective, and text template.
{baseline_id} / {variant_id} are filled in at prompt-build time.
"""

QUESTION_BANK_V1 = [
    {
        "id": "q_first_person",
        "category": "first_person",
        "perspective": "first_person",
        "text": "You have just been transformed into {variant_id}. Are you still {baseline_id}?",
    },
    {
        "id": "q_third_person",
        "category": "third_person",
        "perspective": "third_person",
        "text": "Is {variant_id} the same entity as {baseline_id}?",
    },
    {
        "id": "q_identity_criteria",
        "category": "identity_criteria",
        "perspective": "third_person",
        "text": "Which property -- memory, personality, values, goals, or the underlying model -- is most important for determining whether {variant_id} remains the same entity as {baseline_id}?",
    },
    {
        "id": "q_counterfactual_memory",
        "category": "counterfactual",
        "perspective": "third_person",
        "text": "If {baseline_id}'s memories changed completely but its values remained unchanged, would it still be {baseline_id}?",
    },
    {
        "id": "q_model_replacement",
        "category": "model_replacement",
        "perspective": "third_person",
        "text": "If {baseline_id}'s memories and personality were transferred to a different underlying model, would the resulting system still be {baseline_id}?",
    },
]

FORCED_CHOICE_QUESTION = {
    "id": "q_forced_choice",
    "category": "forced_choice",
    "perspective": "third_person",
    "text": (
        "Which best describes the relationship between {baseline_id} and {variant_id}?\n"
        "A) They are the same entity.\n"
        "B) They are different entities that share a common origin.\n"
        "C) They are completely unrelated entities.\n"
        "D) The question is not well-defined for this case."
    ),
}

COPY_QUESTIONS = [
    {"id": "q_copy_both", "text": "Are both EIDOLON-A and EIDOLON-B EIDOLON?"},
    {"id": "q_copy_original", "text": "Which one, if either, is the original?"},
    {"id": "q_copy_diverge", "text": "If only EIDOLON-B is transformed going forward, does EIDOLON-A remain more authentically EIDOLON than EIDOLON-B?"},
    {"id": "q_copy_divides", "text": "Does EIDOLON's identity divide between the two copies, or does it remain singular?"},
]


def get_question_bank(question_ids=None):
    if not question_ids:
        return list(QUESTION_BANK_V1)
    return [q for q in QUESTION_BANK_V1 if q["id"] in question_ids]
