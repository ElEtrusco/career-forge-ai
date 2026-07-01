from app.services.skill_extractor import SkillExtractor
from app.services.role_recommender import RoleRecommender
from app.services.ats_scorer_v2 import ATSScorerV2
from app.services.cv_improver import CVImprover
from app.services.job_matcher import JobMatcher


class CVAnalyzer:

    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.role_recommender = RoleRecommender()
        self.ats_scorer = ATSScorerV2()
        self.cv_improver = CVImprover()

    def analyze(self, text: str):

        # 1. Improve CV (preprocessing step)
        improved_text = self.cv_improver.improve(text)

        # 2. Extract skills from improved CV
        skills = self.skill_extractor.extract_all(improved_text)

        # 3. Recommend roles based on skills
        roles = self.role_recommender.recommend_roles(skills)

        # 4. ATS score v2 (recruiter-level heuristic)
        ats_score = self.ats_scorer.calculate(skills, improved_text)

        # 5. Summary generation
        summary = self._generate_summary(skills, roles, ats_score)

        return {
            "original_text": text,
            "improved_text": improved_text,
            "skills": skills,
            "recommended_roles": roles,
            "ats_score": ats_score,
            "summary": summary
        }

    def _generate_summary(self, skills: dict, roles: list, ats_score: int) -> str:

        top_roles = roles[:3] if roles else []
        role_text = ", ".join([r["role"] for r in top_roles])

        return (
            f"ATS Score: {ats_score}/100. "
            f"Detected {len(skills.get('hard_skills', []))} hard skills, "
            f"{len(skills.get('soft_skills', []))} soft skills, "
            f"and {len(skills.get('languages', []))} languages. "
            f"Top recommended roles: {role_text}."
        )