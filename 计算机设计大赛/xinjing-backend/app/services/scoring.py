from dataclasses import dataclass


@dataclass
class ScoreResult:
    total: int
    max_score: int
    level: str
    color: str
    desc: str


def calculate_score(scale: str, answers: list[int]) -> ScoreResult:
    scale = scale.lower()

    if scale == "sds":
        reverse_indices = {4, 5, 10, 11, 13, 15, 16, 17, 19}
        raw = 0
        for idx, val in enumerate(answers):
            safe_val = val if val is not None else 1
            raw += (5 - safe_val) if idx in reverse_indices else safe_val
        total = int(raw * 1.25)
        if total < 53:
            return ScoreResult(total, 100, "normal", "#22c55e", "No obvious depressive symptoms.")
        if total <= 62:
            return ScoreResult(total, 100, "mild", "#eab308", "Mild depressive tendency.")
        if total <= 72:
            return ScoreResult(total, 100, "moderate", "#f97316", "Moderate depressive symptoms.")
        return ScoreResult(total, 100, "severe", "#dc2626", "Severe depressive symptoms.")

    if scale == "pss":
        reverse_indices = {3, 4, 6, 7}
        total = 0
        for idx, val in enumerate(answers):
            safe_val = val if val is not None else 0
            total += (4 - safe_val) if idx in reverse_indices else safe_val
        if total <= 13:
            return ScoreResult(total, 40, "low_stress", "#22c55e", "Low stress level.")
        if total <= 26:
            return ScoreResult(total, 40, "mid_stress", "#eab308", "Medium stress level.")
        return ScoreResult(total, 40, "high_stress", "#dc2626", "High stress level.")

    if scale == "ais":
        total = sum(v or 0 for v in answers)
        if total <= 4:
            return ScoreResult(total, 32, "no_insomnia", "#22c55e", "No obvious sleep disorder.")
        if total <= 10:
            return ScoreResult(total, 32, "suspected", "#eab308", "Suspected insomnia.")
        if total <= 14:
            return ScoreResult(total, 32, "mild", "#f97316", "Mild insomnia.")
        if total <= 20:
            return ScoreResult(total, 32, "moderate", "#ef4444", "Moderate insomnia.")
        return ScoreResult(total, 32, "severe", "#dc2626", "Severe insomnia.")

    # default phq9
    total = sum(v or 0 for v in answers)
    if total <= 4:
        return ScoreResult(total, 27, "none", "#22c55e", "No depressive symptoms.")
    if total <= 9:
        return ScoreResult(total, 27, "mild", "#eab308", "Mild depressive symptoms.")
    if total <= 14:
        return ScoreResult(total, 27, "moderate", "#f97316", "Moderate depressive symptoms.")
    if total <= 19:
        return ScoreResult(total, 27, "mod_severe", "#ef4444", "Moderately severe depressive symptoms.")
    return ScoreResult(total, 27, "severe", "#dc2626", "Severe depressive symptoms.")


def build_default_recommendations(scale: str, level: str) -> list[str]:
    common = [
        "Keep regular sleep and wake schedule.",
        "Do light exercise 3 times per week.",
        "Use companion chat for daily emotional support.",
    ]
    if scale == "ais":
        common.insert(0, "Avoid phone usage before sleeping.")
    if "severe" in level:
        common.append("Seek offline professional help as soon as possible.")
    return common
