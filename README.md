# Career Forge AI

> **AI-powered career assistant** para optimizar todo el proceso de búsqueda de empleo: desde el análisis del CV hasta el seguimiento de las candidaturas.

## 📖 Descripción

Career Forge AI es una plataforma que utiliza inteligencia artificial para ayudar a los candidatos a mejorar su perfil profesional, aumentar la compatibilidad con sistemas ATS y agilizar el proceso de búsqueda de empleo.

El objetivo del proyecto es convertirse en un asistente inteligente que acompañe al usuario durante todo el ciclo de búsqueda laboral.

---

## ✨ Características

### 📄 Gestión del CV

* Análisis inteligente del currículum.
* Extracción automática de habilidades.
* Recomendación de perfiles profesionales.
* Optimización para sistemas ATS.
* Generación de versiones personalizadas del CV según la oferta.

### 🤖 Inteligencia Artificial

* Análisis de fortalezas y áreas de mejora.
* Recomendación de palabras clave.
* Generación automática de cartas de presentación.
* Cálculo de coincidencia entre CV y oferta de empleo.
* Sugerencias para mejorar la candidatura.

### 💼 Gestión de candidaturas

* Seguimiento de ofertas.
* Historial de candidaturas.
* Dashboard con métricas.
* Exportación de datos a Excel.

---

## 🏗 Arquitectura

```text
                ┌────────────────────┐
                │     Next.js UI     │
                └──────────┬─────────┘
                           │
                     REST API
                           │
                ┌──────────▼─────────┐
                │      FastAPI       │
                └──────────┬─────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
 CV Services         Job Services      User Services
        │                  │                  │
        └──────────────┬───┴──────────────────┘
                       │
                 OpenAI API
                       │
                 PostgreSQL
```

---

## 🛠 Tecnologías

### Backend

* Python 3.12+
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL
* OpenAI API

### Frontend

* Next.js
* React
* TypeScript

### DevOps

* Docker
* GitHub Actions
* Cloudflare

---

## 📁 Estructura del proyecto

```text
career-forge-ai/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   └── Dockerfile
│
├── frontend/
│
├── README.md
└── LICENSE
```

---

## 🚀 Servicios de IA

El backend está organizado en servicios independientes para facilitar el mantenimiento y la escalabilidad.

| Servicio           | Función                              |
| ------------------ | ------------------------------------ |
| `cv_parser`        | Procesa el CV del usuario            |
| `cv_analyzer`      | Analiza fortalezas y debilidades     |
| `skill_extractor`  | Extrae habilidades automáticamente   |
| `ats_scorer_v2`    | Calcula la puntuación ATS            |
| `job_matcher`      | Evalúa la compatibilidad con ofertas |
| `role_recommender` | Recomienda perfiles profesionales    |
| `cv_improver`      | Genera mejoras para el CV            |

---

## ⚙️ Instalación

### Clonar el repositorio

```bash
git clone https://github.com/ElEtrusco/career-forge-ai.git

cd career-forge-ai
```

### Crear un entorno virtual

```bash
python -m venv .venv
```

### Activar el entorno

Linux / macOS

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

### Instalar dependencias

```bash
pip install -r backend/requirements.txt
```

---

## 🔑 Variables de entorno

Crear un archivo `.env` dentro de `backend`.

Ejemplo:

```env
DATABASE_URL=postgresql://user:password@localhost/careerforge
OPENAI_API_KEY=your_api_key
SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## ▶️ Ejecutar el backend

```bash
cd backend

uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://localhost:8000
```

Documentación interactiva:

```text
http://localhost:8000/docs
```

---

## 🐳 Docker

Construir la imagen:

```bash
docker build -t career-forge-ai .
```

---

## 🗺 Roadmap

### ✅ Implementado

* Estructura base del proyecto
* FastAPI
* Modelos de usuario
* Migraciones con Alembic
* Análisis del CV
* ATS Scoring
* Extracción de habilidades

### 🚧 En desarrollo

* Dashboard
* Autenticación completa
* Generación de CV personalizada
* Cartas de presentación
* Seguimiento de candidaturas
* Exportación a Excel

### 🎯 Futuro

* Matching semántico mediante embeddings
* Integración con portales de empleo
* Recomendaciones personalizadas mediante IA
* Panel de analíticas
* API pública
* Aplicación móvil

---

## 🤝 Contribuir

Las contribuciones son bienvenidas.

1. Haz un fork del proyecto.
2. Crea una rama para tu funcionalidad.
3. Realiza tus cambios.
4. Envía un Pull Request.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.

---

## 👨‍💻 Autor

Desarrollado por **ElEtrusco**.

Si el proyecto te resulta útil, considera darle una ⭐ en GitHub para apoyar su desarrollo.
