import re
from typing import Dict, List


class SkillExtractor:

    def __init__(self):
        self.hard_skills = {
            "python",
            "java",
            "javascript",
            "typescript",
            "fastapi",
            "django",
            "flask",
            "react",
            "nextjs",
            "node",
            "nodejs",
            "postgresql",
            "mysql",
            "mongodb",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "git",
            "github",
            "linux",
            "html",
            "css",
            "rest api",
            "api",
            "microservices",
            "machine learning",
            "deep learning",
            "pandas",
            "numpy",
            "sql",
        }

        self.soft_skills = {
            "teamwork",
            "leadership",
            "communication",
            "problem solving",
            "adaptability",
            "critical thinking",
            "time management",
            "creativity",
            "collaboration",
            "organization",
        }

        self.es_en_map = {
            "trabajo en equipo": "teamwork",
            "colaboración": "collaboration",
            "comunicación": "communication",
            "resolución de problemas": "problem solving",
            "adaptabilidad": "adaptability",
            "pensamiento crítico": "critical thinking",
            "gestión del tiempo": "time management",
            "creatividad": "creativity",
            "organización": "organization",
        }

        self.concept_map = {
            "programación": ["python", "javascript"],
            "desarrollo web": ["html", "css", "javascript"],
            "bases de datos": ["sql", "mysql", "postgresql"],
            "backend": ["python", "fastapi", "django"],
            "frontend": ["html", "css", "javascript", "react"],
            "cloud": ["aws", "azure", "gcp"],
        }

        self.languages = {
            "english": ["english", "inglés", "ingles"],
            "spanish": ["spanish", "español", "espanyol"],
            "french": ["french", "francés", "frances"],
            "german": ["german", "alemán", "aleman"],
            "italian": ["italian", "italiano"],
            "portuguese": ["portuguese", "portugués", "portugues"],
        }

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""

        text = text.lower()
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def extract_hard_skills(
        self,
        text: str,
        expand_concepts: bool = True,
    ) -> List[str]:

        text = self.normalize_text(text)
        found = set()

        for skill in self.hard_skills:

            if skill == "rest api":
                pattern = r"(?<!\w)rest\s+apis?(?!\w)"
            else:
                pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

            if re.search(pattern, text):
                found.add(skill)

        if expand_concepts:
            for concept, skills in self.concept_map.items():
                if re.search(
                    r"(?<!\w)" + re.escape(concept) + r"(?!\w)",
                    text,
                ):
                    found.update(skills)

        return sorted(found)

    def extract_soft_skills(self, text: str) -> List[str]:

        text = self.normalize_text(text)
        found = set()

        for skill in self.soft_skills:
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

            if re.search(pattern, text):
                found.add(skill)

        for es_term, en_term in self.es_en_map.items():
            if re.search(
                r"(?<!\w)" + re.escape(es_term) + r"(?!\w)",
                text,
            ):
                found.add(en_term)

        return sorted(found)

    def extract_languages(self, text: str) -> List[str]:

        text = self.normalize_text(text)
        found = set()

        for language, variants in self.languages.items():

            for variant in variants:

                pattern = r"(?<!\w)" + re.escape(variant) + r"(?!\w)"

                if re.search(pattern, text):
                    found.add(language)
                    break

        return sorted(found)

    def extract_all(
        self,
        text: str,
        expand_concepts: bool = True,
    ) -> Dict[str, List[str]]:

        text = self.normalize_text(text)

        return {
            "hard_skills": self.extract_hard_skills(
                text,
                expand_concepts=expand_concepts,
            ),
            "soft_skills": self.extract_soft_skills(text),
            "languages": self.extract_languages(text),
        }
