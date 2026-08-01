from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = UserService.get_by_email(
        db,
        user_data.email
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = UserService.create_user(
        db,
        user_data
    )

    return user