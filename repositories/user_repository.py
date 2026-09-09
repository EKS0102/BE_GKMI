from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    """
    Repository untuk akses data User.

    Repository hanya bertanggung jawab terhadap operasi data.
    Transaction (commit / rollback) dikelola oleh UnitOfWork.
    """

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # GET USER BY USERNAME
    # =====================================================

    def get_by_username(
        self,
        username: str
    ):
        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )

    # =====================================================
    # GET USER BY EMAIL
    # =====================================================

    def get_by_email(
        self,
        email: str
    ):
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    # =====================================================
    # ADD USER
    # =====================================================

    def add(
        self,
        user: User
    ):
        self.db.add(user)

    # =====================================================
    # REFRESH USER
    # =====================================================

    def refresh(
        self,
        user: User
    ):
        self.db.refresh(user)
        
        
    # =========================================================
    # GET USER BY ID
    # =========================================================

    def get_by_id(
        self,
        user_id: int
    ):
        return (
            self.db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )