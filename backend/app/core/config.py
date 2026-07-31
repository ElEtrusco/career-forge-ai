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
    # OpenAI
    # --------------------------------------------------

    OPENAI_API_KEY: str = Field(...)

    MODEL: str = "gpt-5.5"

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

    # --------------------------------------------------
    # Futuro (RAG / Embeddings)
    # --------------------------------------------------

    EMBEDDING_MODEL: str = "text-embedding-3-large"

    # --------------------------------------------------
    # Configuración de Pydantic
    # --------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Devuelve una única instancia de configuración
    durante toda la vida de la aplicación.
    """
    return Settings()


settings = get_settings()

"""from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Career Forge AI"
    API_VERSION: str = "v1"

    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str

    OPENAI_API_KEY: str

    MODEL: str = "gpt-5.5"

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()"""
