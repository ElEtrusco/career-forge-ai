import re
from typing import Dict, List


class SkillExtractor:

    def __init__(self):

        # -------------------------
        # HARD SKILLS
        # -------------------------
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

        # -------------------------
        # SOFT SKILLS
        # -------------------------
        self.soft_skills = set([
            "teamwork", "leadership",
            "communication", "problem solving",
            "adaptability", "critical thinking",
            "time management", "creativity",
            "collaboration"
        ])

        # -------------------------
        # ES → EN MAPPING (CLAVE)
        # -------------------------
        self.es_en_map = {
            "trabajo en equipo": "teamwork",
            "colaboración": "collaboration",
            "comunicación": "communication",
            "resolución de problemas": "problem solving",
            "adaptabilidad": "adaptability",
            "pensamiento crítico": "critical thinking",
            "gestión del tiempo": "time management",
            "creatividad": "creativity",
            "programación": "python",
            "bases de datos": "mysql"
        }

        # -------------------------
        # LANGUAGES
        # -------------------------
        self.languages = {
            "english": ["english", "inglés", "ingles"],
            "spanish": ["spanish", "español", "espanyol"],
            "french": ["french", "francés", "frances"],
            "german": ["german", "alemán", "aleman"],
            "italian": ["italian", "italiano"],
            "portuguese": ["portuguese", "portugués", "portugues"]
        }

    def normalize_text(self, text: str) -> str:
        return text.lower()

    # -------------------------
    # HARD SKILLS
    # -------------------------
    def extract_hard_skills(self, text: str) -> List[str]:

        found = set()

        for skill in self.hard_skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text):
                found.add(skill)

        return list(found)

    # -------------------------
    # SOFT SKILLS + ES MAPPING
    # -------------------------
    def extract_soft_skills(self, text: str) -> List[str]:

        found = set()

        # direct soft skills
        for skill in self.soft_skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text):
                found.add(skill)

        # ES → EN mapping
        for es_term, en_term in self.es_en_map.items():
            if es_term in text:
                found.add(en_term)

        return list(found)

    # -------------------------
    # LANGUAGES (SMART DETECTION)
    # -------------------------
    def extract_languages(self, text: str) -> List[str]:

        found = set()

        for lang, variants in self.languages.items():
            for v in variants:
                if v in text:
                    found.add(lang)

        # detect levels (B1, B2, C1, etc.)
        if re.search(r"\benglish\s*(a1|a2|b1|b2|c1|c2)\b", text):
            found.add("english")
        if re.search(r"\bfranc[eé]s\s*(a1|a2|b1|b2|c1|c2)\b", text):
            found.add("french")

        return list(found)

    # -------------------------
    # MAIN FUNCTION
    # -------------------------
    def extract_all(self, text: str) -> Dict:

        text = self.normalize_text(text)

        return {
            "hard_skills": self.extract_hard_skills(text),
            "soft_skills": self.extract_soft_skills(text),
            "languages": self.extract_languages(text)
        }