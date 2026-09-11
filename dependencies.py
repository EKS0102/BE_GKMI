from fastapi import Depends
from sqlalchemy.orm import Session

from database.database import SessionLocal
from unit_of_work import UnitOfWork

from services.auth_service import AuthService
from services.jemaat_service import JemaatService
from services.security_cleanup_service import (
    SecurityCleanupService
)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# JEMAAT SERVICE
# =========================================================

def get_jemaat_service(
    db: Session = Depends(get_db)
):
    unit_of_work = UnitOfWork(
        db
    )

    return JemaatService(
        unit_of_work
    )


# =========================================================
# AUTH SERVICE
# =========================================================

def get_auth_service(
    db: Session = Depends(get_db)
):
    unit_of_work = UnitOfWork(
        db
    )

    return AuthService(
        unit_of_work
    )


# =========================================================
# SECURITY CLEANUP SERVICE
# =========================================================

def get_security_cleanup_service(
    db: Session = Depends(get_db)
):
    unit_of_work = UnitOfWork(
        db
    )

    return SecurityCleanupService(
        unit_of_work
    )