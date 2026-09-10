from pathlib import Path
import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config

from main import app
from dependencies import get_db

from models.user import User
from models.jemaat import Jemaat
from models.audit_log import AuditLog
from models.refresh_token import RefreshToken
from models.login_attempt import LoginAttempt


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# TEST DATABASE
# =========================================================

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL"
)

if not TEST_DATABASE_URL:
    raise ValueError(
        "TEST_DATABASE_URL belum diset di file .env"
    )


engine_test = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)


# =========================================================
# ALEMBIC CONFIG
# =========================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

ALEMBIC_INI_PATH = (
    BASE_DIR / "alembic.ini"
)


# =========================================================
# PASSWORD HASH
# =========================================================

password_hash = PasswordHash.recommended()


# =========================================================
# DATABASE FIXTURE
# =========================================================

@pytest.fixture(scope="function")
def db():
    """
    Menyediakan database session untuk setiap test.

    Data dibersihkan sebelum test dimulai.

    Urutan penghapusan:
        RefreshToken
            ↓
        AuditLog
            ↓
        Jemaat
            ↓
        User
    """

    db_session = TestingSessionLocal()

    try:
        # =================================================
        # BERSIHKAN DATA TEST
        # =================================================

        # RefreshToken memiliki FK ke users
        db_session.query(LoginAttempt).delete()
        
        db_session.query(
            RefreshToken
        ).delete()

        # AuditLog memiliki FK ke users
        db_session.query(
            AuditLog
        ).delete()

        # Jemaat tidak memiliki FK ke users
        db_session.query(
            Jemaat
        ).delete()

        # User dihapus paling terakhir
        db_session.query(
            User
        ).delete()

        db_session.commit()

        # =================================================
        # TEST
        # =================================================

        yield db_session

    finally:
        db_session.close()


# =========================================================
# APPLY ALEMBIC MIGRATION
#
# Dijalankan sekali sebelum seluruh test session.
# =========================================================

@pytest.fixture(
    scope="session",
    autouse=True
)
def migrate_test_database():

    alembic_config = Config(
        str(ALEMBIC_INI_PATH)
    )

    # =====================================================
    # ARAHKAN ALEMBIC KE TEST DATABASE
    # =====================================================

    alembic_config.set_main_option(
        "sqlalchemy.url",
        TEST_DATABASE_URL
    )

    # =====================================================
    # MIGRATION SAMPAI HEAD
    # =====================================================

    command.upgrade(
        alembic_config,
        "head"
    )

    yield


# =========================================================
# TEST CLIENT
# =========================================================

@pytest.fixture(scope="function")
def client(db):

    def override_get_db():

        try:
            yield db

        finally:
            pass

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# =========================================================
# CREATE USER HELPER
# =========================================================

def create_user(
    db,
    username: str,
    password: str,
    role: str,
    email: str
):
    """
    Membuat user untuk kebutuhan test.
    """

    hashed_password = password_hash.hash(
        password
    )

    user = User(
        username=username,
        password_hash=hashed_password,
        role=role,
        is_active=True,
        email=email
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =========================================================
# BACKWARD COMPATIBILITY
#
# Digunakan oleh test_auth.py dan test_register.py
# =========================================================

@pytest.fixture
def create_test_user(db):

    return create_user(
        db=db,
        username="admin",
        password="admin123",
        role="admin",
        email="admin@test.com"
    )


# =========================================================
# ADMIN FIXTURE
# =========================================================

@pytest.fixture
def create_admin(db):

    return create_user(
        db=db,
        username="admin",
        password="admin123",
        role="admin",
        email="admin@test.com"
    )


# =========================================================
# STAFF FIXTURE
# =========================================================

@pytest.fixture
def create_staff(db):

    return create_user(
        db=db,
        username="staff",
        password="staff123",
        role="staff",
        email="staff@test.com"
    )


# =========================================================
# VIEWER FIXTURE
# =========================================================

@pytest.fixture
def create_viewer(db):

    return create_user(
        db=db,
        username="viewer",
        password="viewer123",
        role="viewer",
        email="viewer@test.com"
    )


# =========================================================
# LOGIN HELPER
# =========================================================

def get_token(
    client,
    username: str,
    password: str
):
    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.json()[
        "access_token"
    ]


# =========================================================
# ADMIN TOKEN
# =========================================================

@pytest.fixture
def admin_token(
    client,
    create_admin
):
    return get_token(
        client,
        "admin",
        "admin123"
    )


# =========================================================
# STAFF TOKEN
# =========================================================

@pytest.fixture
def staff_token(
    client,
    create_staff
):
    return get_token(
        client,
        "staff",
        "staff123"
    )


# =========================================================
# VIEWER TOKEN
# =========================================================

@pytest.fixture
def viewer_token(
    client,
    create_viewer
):
    return get_token(
        client,
        "viewer",
        "viewer123"
    )