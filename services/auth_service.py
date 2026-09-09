from datetime import datetime, timedelta, UTC

from sqlalchemy.exc import IntegrityError

from pwdlib import PasswordHash

from models.user import User
from models.refresh_token import RefreshToken

from unit_of_work import UnitOfWork

from auth.refresh_token import (
    generate_refresh_token,
    hash_refresh_token
)

from auth.security import create_access_token


# =========================================================
# KONFIGURASI
# =========================================================

REFRESH_TOKEN_EXPIRE_DAYS = 7


# =========================================================
# AUTH SERVICE
# =========================================================

class AuthService:
    """
    Service untuk business logic User / Authentication.

    UnitOfWork menangani:
    - UserRepository
    - RefreshTokenRepository
    - transaction commit
    - transaction rollback
    """

    def __init__(
        self,
        unit_of_work: UnitOfWork
    ):
        self.unit_of_work = unit_of_work
        self.password_hash = PasswordHash.recommended()

    # =====================================================
    # GET USER BY USERNAME
    # =====================================================

    def get_user_by_username(
        self,
        username: str
    ):
        return self.unit_of_work.user.get_by_username(
            username
        )

    # =====================================================
    # GET USER BY EMAIL
    # =====================================================

    def get_user_by_email(
        self,
        email: str
    ):
        return self.unit_of_work.user.get_by_email(
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
            self.unit_of_work.user.add(
                user
            )

            self.unit_of_work.commit()

            self.unit_of_work.user.refresh(
                user
            )

            return user

        except IntegrityError:
            self.unit_of_work.rollback()
            raise

    # =====================================================
    # CREATE REFRESH TOKEN
    # =====================================================

    def create_refresh_token(
        self,
        user_id: int,
        ip_address: str | None = None,
        commit: bool = True
    ) -> str:
        """
        Membuat refresh token.

        Token asli dikembalikan ke client.
        Hash token disimpan ke database.

        commit=False digunakan ketika method dipanggil
        sebagai bagian dari transaction yang lebih besar.
        """

        # =================================================
        # GENERATE TOKEN ASLI
        # =================================================

        raw_token = generate_refresh_token()

        # =================================================
        # HASH TOKEN
        # =================================================

        token_hash = hash_refresh_token(
            raw_token
        )

        # =================================================
        # WAKTU
        # =================================================

        created_at = datetime.now(
            UTC
        )

        expires_at = (
            created_at
            + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        # =================================================
        # MODEL REFRESH TOKEN
        # =================================================

        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked_at=None,
            created_at=created_at,
            ip_address=ip_address
        )

        try:
            self.unit_of_work.refresh_token.add(
                refresh_token
            )

            # =================================================
            # COMMIT OPSIONAL
            # =================================================

            if commit:
                self.unit_of_work.commit()

            return raw_token

        except IntegrityError:
            self.unit_of_work.rollback()
            raise

    # =====================================================
    # LOGIN
    # =====================================================

    def login(
        self,
        username: str,
        password: str,
        ip_address: str | None = None
    ):
        """
        Melakukan proses login.

        Return:
            dict
                jika login berhasil

            None
                jika username/password salah

            "inactive"
                jika user tidak aktif
        """

        # =================================================
        # CARI USER
        # =================================================

        user = self.unit_of_work.user.get_by_username(
            username
        )

        # =================================================
        # USER TIDAK DITEMUKAN
        # =================================================

        if user is None:
            return None

        # =================================================
        # USER TIDAK AKTIF
        # =================================================

        if not user.is_active:
            return "inactive"

        # =================================================
        # VERIFIKASI PASSWORD
        # =================================================

        if not self.password_hash.verify(
            password,
            user.password_hash
        ):
            return None

        # =================================================
        # BUAT ACCESS TOKEN
        # =================================================

        access_token = create_access_token(
            {
                "sub": user.username,
                "role": user.role
            }
        )

        # =================================================
        # BUAT REFRESH TOKEN
        #
        # commit=False supaya refresh token tidak commit
        # sendiri. Login akan melakukan satu commit di akhir.
        # =================================================

        refresh_token = self.create_refresh_token(
            user_id=user.id,
            ip_address=ip_address,
            commit=False
        )

        # =================================================
        # COMMIT SATU TRANSACTION
        # =================================================

        try:
            self.unit_of_work.commit()

        except IntegrityError:
            self.unit_of_work.rollback()
            raise

        # =================================================
        # RETURN TOKEN
        # =================================================

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    # =====================================================
    # REFRESH ACCESS TOKEN - ROTATION
    # =====================================================

    def refresh_access_token(
        self,
        raw_refresh_token: str,
        ip_address: str | None = None
    ):
        """
        Membuat access token baru dengan melakukan
        refresh token rotation.

        Flow:
            1. Cari refresh token aktif
            2. Cari user
            3. Revoke refresh token lama
            4. Buat refresh token baru
            5. Buat access token baru
            6. Commit satu transaction

        Return:
            dict
                jika berhasil

            None
                jika refresh token tidak valid
        """

        # =================================================
        # HASH TOKEN
        # =================================================

        token_hash = hash_refresh_token(
            raw_refresh_token
        )

        # =================================================
        # WAKTU SEKARANG
        # =================================================

        now = datetime.now(
            UTC
        )

        # =================================================
        # CARI TOKEN AKTIF
        # =================================================

        stored_token = (
            self.unit_of_work
            .refresh_token
            .get_active_by_token_hash(
                token_hash,
                now,
                for_update=True
            )
        )

        # =================================================
        # TOKEN TIDAK VALID
        # =================================================

        if stored_token is None:
            return None

        # =================================================
        # CARI USER
        # =================================================

        user = self.unit_of_work.user.get_by_id(
            stored_token.user_id
        )

        # =================================================
        # USER TIDAK DITEMUKAN
        # =================================================

        if user is None:
            return None

        # =================================================
        # USER TIDAK AKTIF
        # =================================================

        if not user.is_active:
            return None

        try:
            # =================================================
            # REVOKE TOKEN LAMA
            # =================================================

            revoked_at = datetime.now(
                UTC
            )

            self.unit_of_work.refresh_token.revoke(
                stored_token,
                revoked_at
            )

            # =================================================
            # BUAT REFRESH TOKEN BARU
            #
            # commit=False karena transaction belum selesai.
            # =================================================

            new_refresh_token = self.create_refresh_token(
                user_id=user.id,
                ip_address=ip_address,
                commit=False
            )

            # =================================================
            # BUAT ACCESS TOKEN BARU
            # =================================================

            access_token = create_access_token(
                {
                    "sub": user.username,
                    "role": user.role
                }
            )

            # =================================================
            # COMMIT SEKALI
            # =================================================

            self.unit_of_work.commit()

        except IntegrityError:
            self.unit_of_work.rollback()
            raise

        # =================================================
        # RETURN TOKEN BARU
        # =================================================

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    # =====================================================
    # REVOKE REFRESH TOKEN
    # =====================================================

    def revoke_refresh_token(
        self,
        raw_refresh_token: str
    ) -> bool:
        """
        Mencabut refresh token.

        Return:
            True
                jika token berhasil dicabut

            False
                jika token tidak ditemukan
                atau sudah pernah dicabut
        """

        # =================================================
        # HASH TOKEN
        # =================================================

        token_hash = hash_refresh_token(
            raw_refresh_token
        )

        # =================================================
        # CARI TOKEN
        # =================================================

        stored_token = (
            self.unit_of_work
            .refresh_token
            .get_by_token_hash(
                token_hash
            )
        )

        # =================================================
        # TOKEN TIDAK DITEMUKAN
        # =================================================

        if stored_token is None:
            return False

        # =================================================
        # TOKEN SUDAH DIREVOKE
        # =================================================

        if stored_token.revoked_at is not None:
            return False

        # =================================================
        # REVOKE TOKEN
        # =================================================

        revoked_at = datetime.now(
            UTC
        )

        self.unit_of_work.refresh_token.revoke(
            stored_token,
            revoked_at
        )

        # =================================================
        # COMMIT
        # =================================================

        try:
            self.unit_of_work.commit()

        except IntegrityError:
            self.unit_of_work.rollback()
            raise

        return True