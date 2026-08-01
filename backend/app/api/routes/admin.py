from fastapi import APIRouter, Depends

from app.api.dependencies import require_admin
from app.models.user import User


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)


@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(require_admin),
):
    return {
        "message": "Welcome to the admin dashboard",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "is_admin": current_user.is_admin,
        },
    }