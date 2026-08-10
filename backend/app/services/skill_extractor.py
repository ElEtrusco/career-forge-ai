from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Set


class SkillExtractor:
    """
    Extractor de habilidades profesional y agnóstico al sector.

    El objetivo de esta clase es detectar habilidades explícitas
    presentes en un texto.

    No intenta decidir si una habilidad es importante para una oferta.
    Esa responsabilidad corresponde a:

        JobKeywordAnalyzer
        JobProfileAnalyzer
        JobMatcher

    SkillExtractor se centra en:

        - hard skills
        - soft skills
        - idiomas
        - certificaciones
        - conceptos profesionales
        - aliases / variantes

    La arquitectura está diseñada para funcionar con diferentes
    sectores profesionales:

        - informática
        - agronomía
        - ingeniería
        - finanzas
        - administración
        - marketing
        - logística
        - recursos humanos
        - salud
        - etc.
    """

    # ==================================================================
    # INITIALIZATION
    # ==================================================================

    def __init__(self) -> None:

        # --------------------------------------------------------------
        # HARD SKILLS
        # --------------------------------------------------------------

        self.hard_skills: Set[str] = {

            # ==========================================================
            # PROGRAMMING / SOFTWARE
            # ==========================================================

            "python",
            "java",
            "javascript",
            "typescript",
            "c",
            "c++",
            "c#",
            "go",
            "golang",
            "rust",
            "php",
            "ruby",
            "kotlin",
            "swift",

            # ==========================================================
            # WEB
            # ==========================================================

            "html",
            "css",
            "sass",
            "scss",
            "react",
            "angular",
            "vue",
            "nextjs",
            "next.js",
            "node",
            "nodejs",
            "express",
            "django",
            "flask",
            "fastapi",

            # ==========================================================
            # DATABASES
            # ==========================================================

            "sql",
            "mysql",
            "postgresql",
            "postgres",
            "mongodb",
            "redis",
            "oracle",
            "sqlite",
            "mariadb",
            "nosql",

            # ==========================================================
            # API / ARCHITECTURE
            # ==========================================================

            "api",
            "rest api",
            "restful api",
            "graphql",
            "microservices",
            "microservices architecture",
            "software architecture",
            "system design",

            # ==========================================================
            # CLOUD
            # ==========================================================

            "aws",
            "amazon web services",
            "azure",
            "microsoft azure",
            "gcp",
            "google cloud",
            "google cloud platform",
            "cloud computing",

            # ==========================================================
            # DEVOPS
            # ==========================================================

            "docker",
            "kubernetes",
            "terraform",
            "ansible",
            "jenkins",
            "github actions",
            "gitlab ci",
            "ci/cd",
            "continuous integration",
            "continuous deployment",

            # ==========================================================
            # VERSION CONTROL
            # ==========================================================

            "git",
            "github",
            "gitlab",
            "bitbucket",

            # ==========================================================
            # OPERATING SYSTEMS
            # ==========================================================

            "linux",
            "windows",
            "macos",
            "unix",

            # ==========================================================
            # DATA / AI
            # ==========================================================

            "machine learning",
            "deep learning",
            "artificial intelligence",
            "natural language processing",
            "computer vision",
            "data science",
            "data analysis",
            "data engineering",
            "pandas",
            "numpy",
            "scipy",
            "scikit-learn",
            "tensorflow",
            "pytorch",
            "keras",
            "matplotlib",
            "power bi",
            "tableau",

            # ==========================================================
            # OFFICE / BUSINESS SOFTWARE
            # ==========================================================

            "excel",
            "microsoft excel",
            "word",
            "powerpoint",
            "microsoft office",
            "google sheets",
            "google workspace",
            "salesforce",
            "sap",
            "oracle erp",

            # ==========================================================
            # AGRONOMY
            # ==========================================================

            "agronomy",
            "agronomia",
            "agriculture",
            "agricultura",
            "precision agriculture",
            "agricultura de precision",
            "precision farming",
            "crop management",
            "gestion de cultivos",
            "soil science",
            "edafologia",
            "soil management",
            "gestion de suelos",
            "irrigation",
            "irrigation management",
            "riego",
            "gestion del riego",
            "fertilization",
            "fertilizacion",
            "crop protection",
            "proteccion de cultivos",
            "plant pathology",
            "fitopatologia",
            "entomology",
            "entomologia",
            "weed management",
            "control de malas hierbas",
            "pest management",
            "control de plagas",
            "greenhouse management",
            "gestion de invernaderos",
            "organic farming",
            "agricultura ecologica",
            "sustainable agriculture",
            "agricultura sostenible",
            "agricultural engineering",
            "ingenieria agronomica",
            "remote sensing",
            "teledeteccion",
            "gis",
            "sig",
            "geographic information systems",
            "sistemas de informacion geografica",
            "yield monitoring",
            "monitoreo de rendimiento",
            "farm management",
            "gestion agricola",
            "agricultural machinery",
            "maquinaria agricola",
            "drone",
            "drones",
            "uav",
            "agricultural drones",
            "fertigation",
            "fertirrigacion",

            # ==========================================================
            # ENGINEERING
            # ==========================================================

            "autocad",
            "solidworks",
            "catia",
            "matlab",
            "simulink",
            "cad",
            "cam",
            "plc",
            "scada",
            "robotics",
            "robotica",
            "industrial automation",
            "automatizacion industrial",
            "quality control",
            "control de calidad",
            "lean manufacturing",
            "six sigma",
            "process engineering",
            "ingenieria de procesos",
            "project engineering",
            "ingenieria de proyectos",

            # ==========================================================
            # FINANCE / ACCOUNTING
            # ==========================================================

            "accounting",
            "contabilidad",
            "financial analysis",
            "analisis financiero",
            "financial modeling",
            "modelizacion financiera",
            "budgeting",
            "presupuestos",
            "forecasting",
            "financial reporting",
            "reporting financiero",
            "audit",
            "auditoria",
            "taxation",
            "fiscalidad",
            "cost accounting",
            "contabilidad de costes",
            "accounts payable",
            "cuentas a pagar",
            "accounts receivable",
            "cuentas a cobrar",

            # ==========================================================
            # MARKETING
            # ==========================================================

            "digital marketing",
            "marketing digital",
            "seo",
            "sem",
            "content marketing",
            "marketing de contenidos",
            "social media",
            "social media marketing",
            "email marketing",
            "google analytics",
            "google ads",
            "meta ads",
            "crm",
            "market research",
            "investigacion de mercados",
            "brand management",
            "gestion de marca",
            "copywriting",
            "ecommerce",
            "e-commerce",

            # ==========================================================
            # LOGISTICS / SUPPLY CHAIN
            # ==========================================================

            "logistics",
            "logistica",
            "supply chain",
            "cadena de suministro",
            "inventory management",
            "gestion de inventario",
            "warehouse management",
            "gestion de almacenes",
            "procurement",
            "compras",
            "purchasing",
            "transport management",
            "gestion del transporte",
            "demand planning",
            "planificacion de demanda",
            "stock management",
            "gestion de stock",

            # ==========================================================
            # HUMAN RESOURCES
            # ==========================================================

            "human resources",
            "recursos humanos",
            "recruitment",
            "seleccion de personal",
            "talent acquisition",
            "adquisicion de talento",
            "talent management",
            "gestion del talento",
            "payroll",
            "nominas",
            "employee relations",
            "relaciones laborales",
            "performance management",
            "gestion del desempeno",

            # ==========================================================
            # HEALTHCARE
            # ==========================================================

            "clinical research",
            "investigacion clinica",
            "patient care",
            "atencion al paciente",
            "healthcare",
            "salud",
            "nursing",
            "enfermeria",
            "pharmacology",
            "farmacologia",
            "laboratory analysis",
            "analisis de laboratorio",
            "medical records",
            "historia clinica",

            # ==========================================================
            # PROJECT MANAGEMENT
            # ==========================================================

            "project management",
            "gestion de proyectos",
            "agile",
            "scrum",
            "kanban",
            "waterfall",
            "jira",
            "confluence",
            "risk management",
            "gestion de riesgos",
            "stakeholder management",
            "gestion de stakeholders",
        }

        # --------------------------------------------------------------
        # SOFT SKILLS
        # --------------------------------------------------------------

        self.soft_skills: Set[str] = {

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
            "decision making",
            "decision-making",
            "attention to detail",
            "analytical thinking",
            "emotional intelligence",
            "negotiation",
            "conflict resolution",
            "planning",
            "proactivity",
            "initiative",
            "customer orientation",
            "results orientation",
            "continuous learning",
            "learning agility",
        }

        # --------------------------------------------------------------
        # SPANISH -> ENGLISH SOFT SKILLS
        # --------------------------------------------------------------

        self.es_en_map = {

            "trabajo en equipo":
                "teamwork",

            "colaboracion":
                "collaboration",

            "colaboración":
                "collaboration",

            "comunicacion":
                "communication",

            "comunicación":
                "communication",

            "resolucion de problemas":
                "problem solving",

            "resolución de problemas":
                "problem solving",

            "adaptabilidad":
                "adaptability",

            "pensamiento critico":
                "critical thinking",

            "pensamiento crítico":
                "critical thinking",

            "gestion del tiempo":
                "time management",

            "gestión del tiempo":
                "time management",

            "creatividad":
                "creativity",

            "organizacion":
                "organization",

            "organización":
                "organization",

            "toma de decisiones":
                "decision making",

            "atencion al detalle":
                "attention to detail",

            "atención al detalle":
                "attention to detail",

            "pensamiento analitico":
                "analytical thinking",

            "pensamiento analítico":
                "analytical thinking",

            "negociacion":
                "negotiation",

            "negociación":
                "negotiation",

            "resolucion de conflictos":
                "conflict resolution",

            "resolución de conflictos":
                "conflict resolution",

            "planificacion":
                "planning",

            "planificación":
                "planning",

            "proactividad":
                "proactivity",

            "iniciativa":
                "initiative",
        }

        # --------------------------------------------------------------
        # CONCEPT MAP
        #
        # Sirve para expandir conceptos generales.
        #
        # Ejemplo:
        #
        # "backend"
        #
        # puede implicar:
        #
        # python
        # fastapi
        # django
        #
        # Esta expansión se mantiene opcional.
        # --------------------------------------------------------------

        self.concept_map = {

            # IT
            "programacion": [
                "python",
                "javascript",
            ],

            "programación": [
                "python",
                "javascript",
            ],

            "desarrollo web": [
                "html",
                "css",
                "javascript",
            ],

            "bases de datos": [
                "sql",
                "mysql",
                "postgresql",
            ],

            "backend": [
                "python",
                "fastapi",
                "django",
            ],

            "frontend": [
                "html",
                "css",
                "javascript",
                "react",
            ],

            "cloud": [
                "aws",
                "azure",
                "gcp",
            ],

            "devops": [
                "docker",
                "kubernetes",
                "ci/cd",
            ],

            "data science": [
                "python",
                "pandas",
                "numpy",
                "scikit-learn",
            ],

            "machine learning": [
                "python",
                "pandas",
                "numpy",
                "scikit-learn",
            ],

            # Agronomy
            "agricultura de precision": [
                "precision agriculture",
                "gis",
                "remote sensing",
            ],

            "agricultura de precisión": [
                "precision agriculture",
                "gis",
                "remote sensing",
            ],

            "precision farming": [
                "precision agriculture",
                "gis",
                "remote sensing",
            ],

            "gestion de cultivos": [
                "crop management",
                "irrigation",
                "fertilization",
            ],

            "gestión de cultivos": [
                "crop management",
                "irrigation",
                "fertilization",
            ],

            "agricultura sostenible": [
                "sustainable agriculture",
                "soil management",
                "crop management",
            ],

            # Business
            "gestion de proyectos": [
                "project management",
                "planning",
                "risk management",
            ],

            "gestión de proyectos": [
                "project management",
                "planning",
                "risk management",
            ],

            "cadena de suministro": [
                "supply chain",
                "logistics",
                "inventory management",
            ],
        }

        # --------------------------------------------------------------
        # LANGUAGES
        # --------------------------------------------------------------

        self.languages = {

            "english": [
                "english",
                "inglés",
                "ingles",
            ],

            "spanish": [
                "spanish",
                "español",
                "espanyol",
                "espanol",
            ],

            "french": [
                "french",
                "francés",
                "frances",
            ],

            "german": [
                "german",
                "alemán",
                "aleman",
            ],

            "italian": [
                "italian",
                "italiano",
            ],

            "portuguese": [
                "portuguese",
                "portugués",
                "portugues",
            ],

            "catalan": [
                "catalan",
                "catalán",
                "valencian",
                "valenciano",
            ],

            "basque": [
                "basque",
                "euskera",
            ],

            "galician": [
                "galician",
                "gallego",
            ],

            "dutch": [
                "dutch",
                "neerlandés",
                "neerlandes",
            ],

            "chinese": [
                "chinese",
                "mandarin",
                "chino",
                "mandarín",
                "mandarin",
            ],

            "japanese": [
                "japanese",
                "japonés",
                "japones",
            ],

            "arabic": [
                "arabic",
                "árabe",
                "arabe",
            ],
        }

        # --------------------------------------------------------------
        # CERTIFICATIONS
        # --------------------------------------------------------------

        self.certifications: Set[str] = {

            # IT
            "aws certified",
            "aws certification",
            "azure certification",
            "google cloud certification",
            "cisco ccna",
            "cisco ccna certification",
            "comptia",
            "comptia security+",
            "comptia security plus",
            "pmp",
            "prince2",
            "scrum master",
            "professional scrum master",
            "psm",
            "certified scrum master",
            "csm",

            # Data / Cloud
            "aws solutions architect",
            "aws developer certification",
            "azure administrator",
            "azure developer",
            "google data analytics",

            # Quality / Management
            "iso 9001",
            "iso 14001",
            "lean six sigma",
            "six sigma green belt",
            "six sigma black belt",

            # Agriculture
            "certified crop advisor",
            "globalgap",
            "global gap",
            "organic certification",
        }

        # --------------------------------------------------------------
        # ALIASES
        #
        # Variantes habituales que deben considerarse equivalentes.
        # --------------------------------------------------------------

        self.aliases = {

            "node.js":
                "nodejs",

            "node js":
                "nodejs",

            "next.js":
                "nextjs",

            "next js":
                "nextjs",

            "postgres":
                "postgresql",

            "postgres sql":
                "postgresql",

            "restful":
                "rest api",

            "rest apis":
                "rest api",

            "k8s":
                "kubernetes",

            "js":
                "javascript",

            "ts":
                "typescript",

            "ml":
                "machine learning",

            "ai":
                "artificial intelligence",

            "artificial intelligence":
                "artificial intelligence",

            "gis":
                "gis",

            "sig":
                "gis",

            "uav":
                "uav",

            "erp":
                "oracle erp",
        }

    # ==================================================================
    # NORMALIZATION
    # ==================================================================

    def normalize_text(
        self,
        text: str,
    ) -> str:
        """
        Normaliza el texto para mejorar la detección.

        Conservamos símbolos importantes como:

            +
            #
            .
            /

        porque aparecen en:

            C++
            C#
            .NET
            CI/CD
            Next.js
        """

        if not text:
            return ""

        text = text.lower()

        # Normalización Unicode.
        text = unicodedata.normalize(
            "NFKD",
            text,
        )

        # Eliminamos únicamente marcas diacríticas.
        text = "".join(
            char
            for char in text
            if not unicodedata.combining(
                char
            )
        )

        # Normalizamos diferentes separadores.
        text = text.replace(
            "\u2013",
            "-",
        )

        text = text.replace(
            "\u2014",
            "-",
        )

        text = text.replace(
            "\u2019",
            "'",
        )

        # Espacios.
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ==================================================================
    # NORMALIZE SKILL
    # ==================================================================

    def normalize_skill(
        self,
        skill: str,
    ) -> str:
        """
        Normaliza una skill individual y aplica aliases.
        """

        normalized = self.normalize_text(
            skill
        )

        normalized = self.aliases.get(
            normalized,
            normalized,
        )

        return normalized

    # ==================================================================
    # GENERIC TERM MATCHING
    # ==================================================================

    def _contains_term(
        self,
        text: str,
        term: str,
    ) -> bool:
        """
        Realiza una búsqueda segura de términos.

        Evita falsos positivos como:

            java

        dentro de:

            javascript
        """

        if not text or not term:
            return False

        term = self.normalize_skill(
            term
        )

        # Casos especiales.
        if term == "rest api":
            pattern = (
                r"(?<!\w)"
                r"rest\s+apis?"
                r"(?!\w)"
            )

        elif term == "c++":
            pattern = (
                r"(?<!\w)"
                r"c\+\+"
                r"(?!\w)"
            )

        elif term == "c#":
            pattern = (
                r"(?<!\w)"
                r"c#"
                r"(?!\w)"
            )

        else:
            pattern = (
                r"(?<!\w)"
                + re.escape(term)
                + r"(?!\w)"
            )

        return (
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
            is not None
        )

    # ==================================================================
    # HARD SKILLS
    # ==================================================================

    def extract_hard_skills(
        self,
        text: str,
        expand_concepts: bool = True,
    ) -> List[str]:
        """
        Extrae hard skills conocidas.

        La detección es explícita y conservadora.
        """

        text = self.normalize_text(
            text
        )

        if not text:
            return []

        found: Set[str] = set()

        for skill in self.hard_skills:

            if self._contains_term(
                text,
                skill,
            ):
                found.add(
                    self.normalize_skill(
                        skill
                    )
                )

        # --------------------------------------------------------------
        # CONCEPT EXPANSION
        # --------------------------------------------------------------

        if expand_concepts:

            for concept, skills in (
                self.concept_map.items()
            ):

                if self._contains_term(
                    text,
                    concept,
                ):

                    for skill in skills:

                        found.add(
                            self.normalize_skill(
                                skill
                            )
                        )

        return sorted(
            found
        )

    # ==================================================================
    # SOFT SKILLS
    # ==================================================================

    def extract_soft_skills(
        self,
        text: str,
    ) -> List[str]:
        """
        Extrae soft skills en inglés y español.
        """

        text = self.normalize_text(
            text
        )

        if not text:
            return []

        found: Set[str] = set()

        # Inglés.
        for skill in self.soft_skills:

            if self._contains_term(
                text,
                skill,
            ):

                found.add(
                    self.normalize_skill(
                        skill
                    )
                )

        # Español.
        for es_term, en_term in (
            self.es_en_map.items()
        ):

            if self._contains_term(
                text,
                es_term,
            ):

                found.add(
                    self.normalize_skill(
                        en_term
                    )
                )

        return sorted(
            found
        )

    # ==================================================================
    # LANGUAGES
    # ==================================================================

    def extract_languages(
        self,
        text: str,
    ) -> List[str]:
        """
        Detecta idiomas mencionados explícitamente.
        """

        text = self.normalize_text(
            text
        )

        if not text:
            return []

        found: Set[str] = set()

        for language, variants in (
            self.languages.items()
        ):

            for variant in variants:

                if self._contains_term(
                    text,
                    variant,
                ):

                    found.add(
                        language
                    )

                    break

        return sorted(
            found
        )

    # ==================================================================
    # CERTIFICATIONS
    # ==================================================================

    def extract_certifications(
        self,
        text: str,
    ) -> List[str]:
        """
        Detecta certificaciones conocidas.

        No intenta inferir certificaciones.
        Solo devuelve aquellas que aparecen explícitamente.
        """

        text = self.normalize_text(
            text
        )

        if not text:
            return []

        found: Set[str] = set()

        for certification in (
            self.certifications
        ):

            if self._contains_term(
                text,
                certification,
            ):

                found.add(
                    self.normalize_skill(
                        certification
                    )
                )

        return sorted(
            found
        )

    # ==================================================================
    # ALL
    # ==================================================================

    def extract_all(
        self,
        text: str,
        expand_concepts: bool = True,
    ) -> Dict[str, List[str]]:
        """
        Extrae todas las categorías disponibles.

        Mantiene las tres claves originales:

            hard_skills
            soft_skills
            languages

        y añade:

            certifications

        Esto mantiene compatibilidad con JobMatcher y permite
        ampliar posteriormente el análisis.
        """

        text = self.normalize_text(
            text
        )

        if not text:
            return {
                "hard_skills": [],
                "soft_skills": [],
                "languages": [],
                "certifications": [],
            }

        return {

            "hard_skills":
                self.extract_hard_skills(
                    text,
                    expand_concepts=expand_concepts,
                ),

            "soft_skills":
                self.extract_soft_skills(
                    text
                ),

            "languages":
                self.extract_languages(
                    text
                ),

            "certifications":
                self.extract_certifications(
                    text
                ),
        }

    # ==================================================================
    # CUSTOM SKILLS
    # ==================================================================

    def add_hard_skills(
        self,
        skills: List[str] | Set[str],
    ) -> None:
        """
        Permite añadir skills dinámicamente.

        Esto será especialmente útil cuando integremos el análisis
        mediante IA/LLM.

        Ejemplo:

            extractor.add_hard_skills([
                "QGIS",
                "ArcGIS",
                "irrigation scheduling",
            ])
        """

        for skill in skills:

            normalized = self.normalize_skill(
                skill
            )

            if normalized:
                self.hard_skills.add(
                    normalized
                )

    def add_soft_skills(
        self,
        skills: List[str] | Set[str],
    ) -> None:
        """
        Añade soft skills dinámicamente.
        """

        for skill in skills:

            normalized = self.normalize_skill(
                skill
            )

            if normalized:
                self.soft_skills.add(
                    normalized
                )

    def add_certifications(
        self,
        certifications: List[str] | Set[str],
    ) -> None:
        """
        Añade certificaciones dinámicamente.
        """

        for certification in (
            certifications
        ):

            normalized = self.normalize_skill(
                certification
            )

            if normalized:
                self.certifications.add(
                    normalized
                )

    def add_concept(
        self,
        concept: str,
        skills: List[str],
    ) -> None:
        """
        Añade un concepto profesional y sus skills asociadas.

        Ejemplo:

            add_concept(
                "agricultura regenerativa",
                [
                    "soil management",
                    "sustainable agriculture",
                ],
            )
        """

        normalized_concept = (
            self.normalize_skill(
                concept
            )
        )

        if not normalized_concept:
            return

        normalized_skills = [
            self.normalize_skill(
                skill
            )
            for skill in skills
            if skill
        ]

        self.concept_map[
            normalized_concept
        ] = sorted(
            set(normalized_skills)
        )


# ======================================================================
# MODULE-LEVEL INSTANCE
# ======================================================================

skill_extractor = SkillExtractor()

