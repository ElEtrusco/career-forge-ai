from typing import Dict, List


class JobMatcher:

    def __init__(self):

        self.skill_map = {
            "python": "python",
            "javascript": "javascript",
            "java": "java",
            "sql": "sql",
            "mysql": "mysql",
            "html": "html",
            "css": "css",
            "fastapi": "fastapi",
            "django": "django",
            "react": "react",
            "node": "node",
            "docker": "docker",
            "git": "git",

            # ES → EN
            "trabajo en equipo": "teamwork",
            "colaboración": "teamwork",
            "comunicación": "communication",
            "adaptabilidad": "adaptability",
            "resolución de problemas": "problem solving",
            "bases de datos": "sql",
            "programación": "programming",
        }

        self.hard_skills_pool = [
            "python", "java", "javascript", "sql", "mysql",
            "fastapi", "django", "react", "node", "aws",
            "docker", "kubernetes", "git"
        ]

        self.soft_skills_pool = [
            "teamwork", "communication", "leadership",
            "problem solving", "adaptability"
        ]

    def normalize(self, text: str) -> str:
        return text.lower()

    def extract_skills_from_text(self, text: str) -> List[str]:

        text = self.normalize(text)

        found = []

        for key, normalized_skill in self.skill_map.items():
            if key in text:
                found.append(normalized_skill)

        return list(set(found))

    def match(self, cv_skills: Dict, job_text: str) -> Dict:

        job_skills = self.extract_skills_from_text(job_text)

        cv_hard = set(cv_skills.get("hard_skills", []))
        cv_soft = set(cv_skills.get("soft_skills", []))

        job_set = set(job_skills)

        # -------------------------
        # HARD / SOFT separation
        # -------------------------
        job_hard = job_set & set(self.hard_skills_pool)
        job_soft = job_set & set(self.soft_skills_pool)

        cv_hard_match = cv_hard & job_hard
        cv_soft_match = cv_soft & job_soft

        # -------------------------
        # SCORE (RESTAURADO + MEJORADO)
        # -------------------------
        hard_score = (len(cv_hard_match) / len(job_hard)) * 70 if job_hard else 0
        soft_score = (len(cv_soft_match) / len(job_soft)) * 30 if job_soft else 0

        score = round(min(hard_score + soft_score, 100), 2)

        # -------------------------
        # GAP ANALYSIS
        # -------------------------
        missing_skills = list(job_hard - cv_hard)

        return {
            "match_score": score,
            "hard_match": list(cv_hard_match),
            "soft_match": list(cv_soft_match),
            "missing_skills": missing_skills,
            "job_skills_detected": job_skills
        }