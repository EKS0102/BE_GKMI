from datetime import UTC, datetime, timedelta

from models.login_attempt import LoginAttempt
from repositories.login_attempt_repository import (
    LoginAttemptRepository
)


# =========================================================
# ADD
# =========================================================

def test_add_login_attempt(db):

    repository = LoginAttemptRepository(
        db
    )

    now = datetime.now(
        UTC
    )

    attempt = LoginAttempt(
        username="admin",
        ip_address="127.0.0.1",
        failed_at=now,
        created_at=now
    )

    repository.add(
        attempt
    )

    db.commit()

    result = (
        db.query(LoginAttempt)
        .filter(
            LoginAttempt.username == "admin"
        )
        .first()
    )

    assert result is not None
    assert result.username == "admin"
    assert result.ip_address == "127.0.0.1"


# =========================================================
# COUNT RECENT FAILED ATTEMPTS
# =========================================================

def test_count_recent_failed_attempts(
    db
):

    repository = LoginAttemptRepository(
        db
    )

    now = datetime.now(
        UTC
    )

    attempts = [
        LoginAttempt(
            username="admin",
            ip_address="127.0.0.1",
            failed_at=now,
            created_at=now
        ),
        LoginAttempt(
            username="admin",
            ip_address="127.0.0.1",
            failed_at=now,
            created_at=now
        ),
        LoginAttempt(
            username="admin",
            ip_address="127.0.0.1",
            failed_at=now,
            created_at=now
        )
    ]

    for attempt in attempts:
        repository.add(
            attempt
        )

    db.commit()

    since = (
        now
        - timedelta(
            minutes=15
        )
    )

    count = repository.count_recent_failed_attempts(
        username="admin",
        ip_address="127.0.0.1",
        since=since
    )

    assert count == 3


# =========================================================
# COUNT BY DIFFERENT USERNAME
# =========================================================

def test_count_recent_failed_attempts_different_username(
    db
):

    repository = LoginAttemptRepository(
        db
    )

    now = datetime.now(
        UTC
    )

    repository.add(
        LoginAttempt(
            username="admin",
            ip_address="127.0.0.1",
            failed_at=now,
            created_at=now
        )
    )

    repository.add(
        LoginAttempt(
            username="staff",
            ip_address="127.0.0.1",
            failed_at=now,
            created_at=now
        )
    )

    db.commit()

    since = (
        now
        - timedelta(
            minutes=15
        )
    )

    count = repository.count_recent_failed_attempts(
        username="admin",
        ip_address="127.0.0.1",
        since=since
    )

    assert count == 1


# =========================================================
# GET RECENT FAILED ATTEMPTS
# =========================================================

def test_get_recent_failed_attempts(
    db
):

    repository = LoginAttemptRepository(
        db
    )

    now = datetime.now(
        UTC
    )

    repository.add(
        LoginAttempt(
            username="admin",
            ip_address="127.0.0.1",
            failed_at=now,
            created_at=now
        )
    )

    repository.add(
        LoginAttempt(
            username="admin",
            ip_address="127.0.0.1",
            failed_at=now - timedelta(
                minutes=1
            ),
            created_at=now - timedelta(
                minutes=1
            )
        )
    )

    db.commit()

    since = (
        now
        - timedelta(
            minutes=15
        )
    )

    results = repository.get_recent_failed_attempts(
        username="admin",
        ip_address="127.0.0.1",
        since=since
    )

    assert len(results) == 2

    assert results[0].username == "admin"
    assert results[1].username == "admin"


# =========================================================
# DELETE OLD ATTEMPTS
# =========================================================

def test_delete_older_than(
    db
):

    repository = LoginAttemptRepository(
        db
    )

    now = datetime.now(
        UTC
    )

    old_attempt = LoginAttempt(
        username="admin",
        ip_address="127.0.0.1",
        failed_at=now - timedelta(
            days=2
        ),
        created_at=now - timedelta(
            days=2
        )
    )

    recent_attempt = LoginAttempt(
        username="admin",
        ip_address="127.0.0.1",
        failed_at=now,
        created_at=now
    )

    repository.add(
        old_attempt
    )

    repository.add(
        recent_attempt
    )

    db.commit()

    deleted = repository.delete_older_than(
        before=now - timedelta(
            days=1
        )
    )

    db.commit()

    assert deleted == 1

    remaining = (
        db.query(LoginAttempt)
        .all()
    )

    assert len(remaining) == 1

    assert remaining[0].created_at == (
        recent_attempt.created_at
    )