import re


TECH_SKILLS = [
    "python", "sql", "mysql", "javascript", "php",
    "fastapi", "django", "html", "css", "git",
    "linux", "api", "docker"
]


def analyze_cv(text: str):

    text_lower = text.lower()

    found_skills = [
        skill for skill in TECH_SKILLS
        if skill in text_lower
    ]

    # inferencia simple de rol
    if "python" in found_skills and "sql" in found_skills:
        role = "Junior Data / Backend Developer"
    elif "javascript" in found_skills:
        role = "Frontend / Fullstack Junior"
    else:
        role = "IT Junior Support / Entry Level"

    # scoring básico
    score = len(found_skills) * 10

    return {
        "skills_detected": found_skills,
        "recommended_role": role,
        "ats_score": min(score, 100),
        "profile_level": "junior"
    }