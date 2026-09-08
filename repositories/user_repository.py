from sqlalchemy.orm import Session

from models.user import User


# =========================================================
# USER REPOSITORY
# =========================================================

class UserRepository:
    """
    Repository untuk seluruh akses database User.
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
    # COMMIT
    # =====================================================

    def commit(self):
        self.db.commit()

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(self):
        self.db.rollback()

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self,
        user: User
    ):
        self.db.refresh(user)