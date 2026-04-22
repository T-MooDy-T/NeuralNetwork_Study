import os
os.environ["DATABASE_URL"] = "sqlite:///./campus_ai.db"

from app.database.connection import get_db
from app.database.models import User

db = next(get_db())
users = db.query(User).all()
print(f"数据库中用户数: {len(users)}")
for u in users:
    print(f"{u.id}: {u.username} ({u.nickname})")