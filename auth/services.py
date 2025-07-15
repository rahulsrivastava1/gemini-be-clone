from sqlalchemy.orm import Session

from auth.models import Users
from auth.schemas import UsersCreate


def create_user(db: Session, user: UsersCreate):
    """
    Create a new user with the provided information
    """
    # Check if user with this phone number already exists
    existing_user = db.query(Users).filter(Users.phone == user.phone).first()
    if existing_user:
        raise ValueError("User with this phone number already exists")

    # Create new user
    db_user = Users(phone=user.phone)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
