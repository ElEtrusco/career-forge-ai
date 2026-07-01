import re
from typing import Dict


class ATSScorerV2:

    def calculate(self, skills: Dict, text: str) -> int:

        text_lower = text.lower()
        score = 0

        # -------------------------
        # 1. SKILL DENSITY (30 pts)
        # -------------------------
        hard = len(skills.get("hard_skills", []))
        soft = len(skills.get("soft_skills", []))
        lang = len(skills.get("languages", []))

        score += min(hard * 5, 20)
        score += min(soft * 2, 6)
        score += min(lang * 2, 4)

        # -------------------------
        # 2. CV STRUCTURE (25 pts)
        # -------------------------
        sections = ["experience", "education", "skills", "projects", "work"]

        structure_score = sum(1 for s in sections if s in text_lower)
        score += structure_score * 5

        # -------------------------
        # 3. IMPACT / NUMBERS (15 pts)
        # -------------------------
        numbers = len(re.findall(r"\d+", text_lower))
        score += min(numbers * 1, 15)

        # -------------------------
        # 4. ACTION VERBS (15 pts)
        # -------------------------
        verbs = [
            "developed", "built", "led", "designed",
            "created", "implemented", "optimized"
        ]

        verb_score = sum(1 for v in verbs if v in text_lower)
        score += verb_score * 3

        # -------------------------
        # 5. PENALTIES (15 pts)
        # -------------------------
        penalty = 0

        if len(text_lower) < 1000:
            penalty += 5

        if "experience" not in text_lower:
            penalty += 5

        if hard == 0:
            penalty += 5

        score -= penalty

        # -------------------------
        # FINAL CAP
        # -------------------------
        return max(0, min(score, 100))