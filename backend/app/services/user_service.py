from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from app.core.security import verify_password


class UserService:

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ) -> User | None:

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )


    @staticmethod
    def create_user(
        db: Session,
        user_data: UserCreate
    ) -> User:

        hashed_password = hash_password(
            user_data.password
        )

        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ):
        user = UserService.get_by_email(
            db,
            email
        )

        if not user:
            return None

        if not verify_password(
            password,
            user.hashed_password
        ):
            return None

        return user
    
 @staticmethod
    def get_by_id(
        db: Session,
        user_id: int
    ) -> User | None:

        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )   