from sqlalchemy.orm import Session


class UnitOfWork:
    """
    Mengelola transaction pada SQLAlchemy Session.

    Session diberikan dari luar sehingga Repository
    dan UnitOfWork menggunakan session yang sama.
    """

    def __init__(
        self,
        session: Session
    ):
        self.session = session

    # =====================================================
    # COMMIT
    # =====================================================

    def commit(self):
        self.session.commit()

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(self):
        self.session.rollback()