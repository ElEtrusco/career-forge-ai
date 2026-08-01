from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
)
from app.services.user_service import UserService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.security import create_access_token


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

@router.post(
    "/login",
    response_model=Token
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):

    user = UserService.authenticate_user(
        db,
        credentials.email,
        credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
):
    return current_user