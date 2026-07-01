from typing import Dict, List


class RoleRecommender:

    def __init__(self):

        # Mapa de roles → skills necesarias (base realista)
        self.role_map = {
            "Backend Developer": {
                "must": ["python", "fastapi", "django", "flask", "api", "rest api"],
                "nice": ["docker", "postgresql", "mysql", "aws", "microservices"]
            },
            "Frontend Developer": {
                "must": ["javascript", "react", "nextjs", "html", "css"],
                "nice": ["typescript", "redux", "tailwind"]
            },
            "Full Stack Developer": {
                "must": ["javascript", "python"],
                "nice": ["react", "fastapi", "nodejs", "docker"]
            },
            "Data Analyst": {
                "must": ["python", "pandas", "numpy"],
                "nice": ["sql", "power bi", "excel", "tableau"]
            },
            "Data Scientist": {
                "must": ["python", "machine learning", "pandas", "numpy"],
                "nice": ["deep learning", "tensorflow", "pytorch"]
            },
            "DevOps Engineer": {
                "must": ["docker", "kubernetes", "aws", "linux"],
                "nice": ["ci/cd", "terraform", "jenkins"]
            },
            "AI Engineer": {
                "must": ["python", "machine learning"],
                "nice": ["deep learning", "nlp", "pytorch", "tensorflow"]
            },
            "Software Engineer": {
                "must": ["python", "java", "javascript"],
                "nice": ["git", "docker", "apis"]
            }
        }

    def recommend_roles(self, skills: Dict) -> List[Dict]:

        all_skills = set()

        # unificar skills
        for category in skills.values():
            if isinstance(category, list):
                all_skills.update([s.lower() for s in category])

        results = []

        for role, requirements in self.role_map.items():

            must = requirements["must"]
            nice = requirements["nice"]

            must_score = self._calculate_match(all_skills, must)
            nice_score = self._calculate_match(all_skills, nice)

            final_score = (must_score * 0.7) + (nice_score * 0.3)

            if must_score > 0:  # mínimo viable
                results.append({
                    "role": role,
                    "match_score": round(final_score, 2),
                    "must_match": must_score,
                    "nice_match": nice_score
                })

        # ordenar por mejor match
        results.sort(key=lambda x: x["match_score"], reverse=True)

        return results

    def _calculate_match(self, user_skills: set, required_skills: List[str]) -> float:

        if not required_skills:
            return 0

        matches = 0

        for skill in required_skills:
            if skill.lower() in user_skills:
                matches += 1

        return (matches / len(required_skills)) * 100