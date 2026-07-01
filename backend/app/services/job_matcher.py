import re
from typing import Dict, List


class JobMatcher:

    def extract_job_skills(self, job_text: str) -> Dict:
        text = job_text.lower()

        hard_skills_pool = [
            "python", "java", "javascript", "sql", "mysql",
            "fastapi", "django", "react", "node", "aws",
            "docker", "kubernetes", "git"
        ]

        soft_skills_pool = [
            "teamwork", "communication", "leadership",
            "problem solving", "adaptability"
        ]

        found_hard = [s for s in hard_skills_pool if s in text]
        found_soft = [s for s in soft_skills_pool if s in text]

        return {
            "hard_skills": found_hard,
            "soft_skills": found_soft
        }

    def match(self, cv_skills: Dict, job_text: str) -> Dict:

        job_skills = self.extract_job_skills(job_text)

        cv_hard = set(cv_skills.get("hard_skills", []))
        cv_soft = set(cv_skills.get("soft_skills", []))

        job_hard = set(job_skills.get("hard_skills", []))
        job_soft = set(job_skills.get("soft_skills", []))

        # -------------------------
        # MATCH CORE SCORE
        # -------------------------
        hard_match = len(cv_hard & job_hard)
        soft_match = len(cv_soft & job_soft)

        must_match = len(job_hard) if job_hard else 1

        score = (hard_match / must_match) * 70 + (soft_match * 5)

        score = min(round(score, 2), 100)

        # -------------------------
        # GAP ANALYSIS
        # -------------------------
        missing_skills = list(job_hard - cv_hard)

        return {
            "match_score": score,
            "hard_match": list(cv_hard & job_hard),
            "soft_match": list(cv_soft & job_soft),
            "missing_skills": missing_skills,
            "job_skills": job_skills
        }