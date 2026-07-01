import re
from typing import Dict, List


class SkillExtractor:

    def __init__(self):
        # Hard skills base (extensible)
        self.hard_skills = set([
            "python", "java", "javascript", "typescript",
            "fastapi", "django", "flask",
            "react", "nextjs", "node", "nodejs",
            "postgresql", "mysql", "mongodb",
            "docker", "kubernetes",
            "aws", "azure", "gcp",
            "git", "github",
            "linux",
            "html", "css",
            "rest api", "api", "microservices",
            "machine learning", "deep learning",
            "pandas", "numpy"
        ])

        # Soft skills base
        self.soft_skills = set([
            "teamwork", "leadership",
            "communication", "problem solving",
            "adaptability", "critical thinking",
            "time management", "creativity",
            "collaboration"
        ])

        # Languages patterns
        self.languages = [
            "english", "spanish", "french",
            "german", "italian", "portuguese"
        ]

    def normalize_text(self, text: str) -> str:
        return text.lower()

    def extract_hard_skills(self, text: str) -> List[str]:
        found = []

        for skill in self.hard_skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text):
                found.append(skill)

        return list(set(found))

    def extract_soft_skills(self, text: str) -> List[str]:
        found = []

        for skill in self.soft_skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text):
                found.append(skill)

        return list(set(found))

    def extract_languages(self, text: str) -> List[str]:
        found = []

        for lang in self.languages:
            if lang in text:
                found.append(lang)

        return list(set(found))

    def extract_all(self, text: str) -> Dict:

        text = self.normalize_text(text)

        return {
            "hard_skills": self.extract_hard_skills(text),
            "soft_skills": self.extract_soft_skills(text),
            "languages": self.extract_languages(text)
        }