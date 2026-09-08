from sqlalchemy.exc import IntegrityError

from models.user import User
from repositories.user_repository import UserRepository
from unit_of_work import UnitOfWork


# =========================================================
# AUTH SERVICE
# =========================================================

class AuthService:
    """
    Service untuk business logic User / Authentication.

    Repository menangani akses data.
    UnitOfWork menangani transaction.
    """

    def __init__(
        self,
        repository: UserRepository,
        unit_of_work: UnitOfWork
    ):
        self.repository = repository
        self.unit_of_work = unit_of_work

    # =====================================================
    # GET USER BY USERNAME
    # =====================================================

    def get_user_by_username(
        self,
        username: str
    ):
        return self.repository.get_by_username(
            username
        )

    # =====================================================
    # GET USER BY EMAIL
    # =====================================================

    def get_user_by_email(
        self,
        email: str
    ):
        return self.repository.get_by_email(
            email
        )

    # =====================================================
    # CREATE USER
    # =====================================================

    def create_user(
        self,
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
            self.repository.add(
                user
            )

            self.unit_of_work.commit()

            self.repository.refresh(
                user
            )

            return user

        except IntegrityError:
            self.unit_of_work.rollback()
            raise