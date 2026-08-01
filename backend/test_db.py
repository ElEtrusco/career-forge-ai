from app.database.session import SessionLocal
from app.models.user import User


db = SessionLocal()

user = User(
    name="Test User",
    email="test@example.com",
    hashed_password="hash123"
)

db.add(user)
db.commit()
db.refresh(user)

print(user.id)
print(user.created_at)

db.close()