from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import decode_access_token
from app.core.config import settings

from app.services.user_service import UserService
from app.services.ai_service import AIService

from app.llm.ollama_provider import OllamaProvider

from app.models.user import User



oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)



# --------------------------------------------------
# Usuarios
# --------------------------------------------------


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    payload = decode_access_token(token)


    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


    user_id = payload.get("sub")


    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
        )


    user = UserService.get_by_id(
        db,
        int(user_id),
    )


    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )


    return user




def require_admin(
    current_user: User = Depends(get_current_user),
):

    if not current_user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Administrator privileges required",
        )


    return current_user




# --------------------------------------------------
# IA
# --------------------------------------------------


def get_llm_provider():

    provider = settings.LLM_PROVIDER.lower()



    if provider == "ollama":

        return OllamaProvider()



    # Preparado para futuros proveedores
    #
    # elif provider == "openai":
    #
    #     return OpenAIProvider()
    #
    #
    # elif provider == "gemini":
    #
    #     return GeminiProvider()



    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )




def get_ai_service() -> AIService:
    """
    Crea el servicio AI con el proveedor configurado.
    """

    llm = get_llm_provider()


    return AIService(
        llm=llm
    )
