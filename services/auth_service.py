from sqlalchemy.orm import Session

from models.user import User


def get_user_by_username(db: Session, username: str):
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def create_user(
    db: Session,
    username: str,
    password_hash: str,
    role: str
):
    user = User(
        username=username,
        password_hash=password_hash,
        role=role,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user