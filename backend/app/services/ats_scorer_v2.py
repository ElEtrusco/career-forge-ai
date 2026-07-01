import re
from typing import Dict


class ATSScorerV2:

    def calculate(self, skills: Dict, text: str) -> int:

        text_lower = text.lower()
        score = 0

        hard = len(skills.get("hard_skills", []))
        soft = len(skills.get("soft_skills", []))
        languages = len(skills.get("languages", []))

        # --------------------------------------------------
        # 1. HARD SKILLS (30 puntos)
        # --------------------------------------------------
        score += min(hard * 4, 30)

        # --------------------------------------------------
        # 2. SOFT SKILLS (10 puntos)
        # --------------------------------------------------
        score += min(soft * 2, 10)

        # --------------------------------------------------
        # 3. IDIOMAS (10 puntos)
        # --------------------------------------------------
        score += min(languages * 3, 10)

        # --------------------------------------------------
        # 4. ESTRUCTURA DEL CV (20 puntos)
        # Compatible ES / EN
        # --------------------------------------------------
        sections = [
            ["experience", "experiencia"],
            ["education", "formación", "formacion"],
            ["skills", "competencias"],
            ["projects", "proyectos"],
            ["languages", "idiomas"]
        ]

        structure_score = 0

        for variants in sections:
            if any(v in text_lower for v in variants):
                structure_score += 4

        score += structure_score

        # --------------------------------------------------
        # 5. NÚMEROS / MÉTRICAS (10 puntos)
        # --------------------------------------------------
        numbers = len(re.findall(r"\d+", text_lower))
        score += min(numbers, 10)

        # --------------------------------------------------
        # 6. VERBOS DE ACCIÓN ES / EN (20 puntos)
        # --------------------------------------------------
        action_verbs = [

            # Inglés
            "developed",
            "built",
            "created",
            "implemented",
            "optimized",
            "designed",
            "led",
            "managed",
            "improved",
            "automated",

            # Español
            "desarrolló",
            "desarrollado",
            "implementó",
            "implementado",
            "gestionó",
            "gestionado",
            "lideró",
            "creó",
            "creado",
            "optimizó",
            "optimizó",
            "analizó",
            "diseñó",
            "mantuvo",
            "coordinó"
        ]

        verbs_found = 0

        for verb in action_verbs:
            if verb in text_lower:
                verbs_found += 1

        score += min(verbs_found * 2, 20)

        # --------------------------------------------------
        # 7. PENALIZACIONES
        # --------------------------------------------------
        penalties = 0

        if len(text_lower) < 800:
            penalties += 5

        if hard < 3:
            penalties += 5

        if not any(
            section in text_lower
            for section in [
                "experience",
                "experiencia"
            ]
        ):
            penalties += 5

        score -= penalties

        # --------------------------------------------------
        # SCORE FINAL
        # --------------------------------------------------
        score = max(0, min(int(round(score)), 100))

        return score