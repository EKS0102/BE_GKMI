from sqlalchemy.orm import Session

from models.jemaat import Jemaat


class JemaatRepository:
    """
    Repository untuk seluruh akses database Jemaat.
    """

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # GET QUERY
    # =====================================================

    def get_query(self):
        return self.db.query(Jemaat)

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        jemaat_id: int
    ):
        return (
            self.db.query(Jemaat)
            .filter(Jemaat.id == jemaat_id)
            .first()
        )

    # =====================================================
    # ADD ONE
    # =====================================================

    def add(
        self,
        data: Jemaat
    ):
        self.db.add(data)

    # =====================================================
    # ADD MANY
    # =====================================================

    def add_many(
        self,
        data_list: list[Jemaat]
    ):
        self.db.add_all(data_list)

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        data: Jemaat
    ):
        self.db.delete(data)

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
        data: Jemaat
    ):
        self.db.refresh(data)

    # =====================================================
    # REFRESH MANY
    # =====================================================

    def refresh_many(
        self,
        data_list: list[Jemaat]
    ):
        for data in data_list:
            self.db.refresh(data)