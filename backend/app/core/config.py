from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración global de Career Forge AI.
    Todos los valores se cargan desde el archivo .env.
    """

    # --------------------------------------------------
    # Aplicación
    # --------------------------------------------------

    APP_NAME: str = "Career Forge AI"
    API_VERSION: str = "v1"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8000


    # --------------------------------------------------
    # Base de datos
    # --------------------------------------------------

    DATABASE_URL: str = Field(...)


    # --------------------------------------------------
    # IA - Proveedor activo
    # --------------------------------------------------

    LLM_PROVIDER: str = "ollama"


    # --------------------------------------------------
    # OpenAI
    # --------------------------------------------------

    OPENAI_API_KEY: str = Field(default="")

    OPENAI_MODEL: str = "gpt-5.5"


    # --------------------------------------------------
    # Ollama
    # --------------------------------------------------

    OLLAMA_URL: str = "http://localhost:11434"

    OLLAMA_MODEL: str = "llama3.2:3b"


    # --------------------------------------------------
    # Google Gemini
    # --------------------------------------------------

    GEMINI_API_KEY: str = Field(default="")

    GEMINI_MODEL: str = "gemini-2.5-pro"


    # --------------------------------------------------
    # Anthropic Claude
    # --------------------------------------------------

    ANTHROPIC_API_KEY: str = Field(default="")

    CLAUDE_MODEL: str = "claude-sonnet-4"


    # --------------------------------------------------
    # Embeddings
    # --------------------------------------------------

    EMBEDDING_MODEL: str = "text-embedding-3-large"


    # --------------------------------------------------
    # Seguridad
    # --------------------------------------------------

    SECRET_KEY: str = Field(...)

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    # --------------------------------------------------
    # Logging
    # --------------------------------------------------

    LOG_LEVEL: str = "INFO"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
