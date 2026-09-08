import hashlib
import secrets


# =========================================================
# GENERATE REFRESH TOKEN
# =========================================================

def generate_refresh_token() -> str:
    """
    Menghasilkan refresh token acak yang aman.
    """

    return secrets.token_urlsafe(64)


# =========================================================
# HASH REFRESH TOKEN
# =========================================================

def hash_refresh_token(
    token: str
) -> str:
    """
    Menghasilkan SHA-256 hash dari refresh token.

    Token asli tidak disimpan di database.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()