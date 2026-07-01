import re


class CVImprover:

    def improve(self, text: str) -> str:

        improved = text

        # -------------------------
        # 1. Normalize weak verbs
        # -------------------------
        replacements = {
            "worked on": "developed",
            "helped with": "contributed to",
            "responsible for": "led",
            "did": "implemented",
        }

        for k, v in replacements.items():
            improved = re.sub(k, v, improved, flags=re.IGNORECASE)

        # -------------------------
        # 2. Add implicit impact phrasing
        # -------------------------
        improved = re.sub(
            r"(developed|built|created)",
            r"\1 scalable and optimized",
            improved,
            flags=re.IGNORECASE
        )

        # -------------------------
        # 3. Basic ATS keyword boost (light touch)
        # -------------------------
        keywords = "optimized for scalability, performance, and maintainability"

        if "fastapi" in improved.lower():
            improved += f"\n\nExperience includes {keywords} using FastAPI architecture."

        return improved