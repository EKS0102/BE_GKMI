from unittest.mock import Mock

import pytest

from services.security_cleanup_service import (
    SecurityCleanupService,
    LOGIN_ATTEMPT_RETENTION_DAYS
)


# =========================================================
# HELPER
# =========================================================

def create_service():
    unit_of_work = Mock()

    service = SecurityCleanupService(
        unit_of_work
    )

    return service, unit_of_work


# =========================================================
# CLEANUP REFRESH TOKENS - SUCCESS
# =========================================================

def test_cleanup_refresh_tokens_success():

    service, unit_of_work = create_service()

    unit_of_work.refresh_token.delete_invalid_tokens.return_value = 3

    result = service.cleanup_refresh_tokens()

    assert result == 3

    unit_of_work.refresh_token.delete_invalid_tokens.assert_called_once()

    now = (
        unit_of_work
        .refresh_token
        .delete_invalid_tokens
        .call_args
        .args[0]
    )

    assert now.tzinfo is not None

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# CLEANUP REFRESH TOKENS - ERROR
# =========================================================

def test_cleanup_refresh_tokens_error():

    service, unit_of_work = create_service()

    unit_of_work.refresh_token.delete_invalid_tokens.side_effect = (
        Exception("database error")
    )

    with pytest.raises(Exception):

        service.cleanup_refresh_tokens()

    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


# =========================================================
# CLEANUP LOGIN ATTEMPTS - SUCCESS
# =========================================================

def test_cleanup_login_attempts_success():

    service, unit_of_work = create_service()

    unit_of_work.login_attempt.delete_older_than.return_value = 5

    result = service.cleanup_login_attempts()

    assert result == 5

    unit_of_work.login_attempt.delete_older_than.assert_called_once()

    before = (
        unit_of_work
        .login_attempt
        .delete_older_than
        .call_args
        .args[0]
    )

    assert before.tzinfo is not None

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# CLEANUP LOGIN ATTEMPTS - ERROR
# =========================================================

def test_cleanup_login_attempts_error():

    service, unit_of_work = create_service()

    unit_of_work.login_attempt.delete_older_than.side_effect = (
        Exception("database error")
    )

    with pytest.raises(Exception):

        service.cleanup_login_attempts()

    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


# =========================================================
# CLEANUP ALL - SUCCESS
# =========================================================

def test_cleanup_all():

    service, unit_of_work = create_service()

    # Mock kedua method service agar kita fokus
    # pada orchestration cleanup_all().
    service.cleanup_refresh_tokens = Mock(
        return_value=3
    )

    service.cleanup_login_attempts = Mock(
        return_value=7
    )

    result = service.cleanup_all()

    assert result == {
        "refresh_tokens_deleted": 3,
        "login_attempts_deleted": 7
    }

    service.cleanup_refresh_tokens.assert_called_once()

    service.cleanup_login_attempts.assert_called_once()