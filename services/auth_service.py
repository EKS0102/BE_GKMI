from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.user import User


# =========================================================
# GET USER BY USERNAME
# =========================================================

def get_user_by_username(
    db: Session,
    username: str
):
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


# =========================================================
# GET USER BY EMAIL
# =========================================================

def get_user_by_email(
    db: Session,
    email: str
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


# =========================================================
# CREATE USER
# =========================================================

def create_user(
    db: Session,
    username: str,
    password_hash: str,
    role: str,
    email: str
):
    user = User(
        username=username,
        password_hash=password_hash,
        role=role,
        is_active=True,
        email=email
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except IntegrityError:
        db.rollback()
        raise