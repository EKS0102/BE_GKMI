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
    
# =========================================================
# FILTER USERNAME + IP
# =========================================================

def test_get_recent_failed_attempts_filters_username_and_ip(
    db
):
    from datetime import datetime, timedelta, UTC

    from models.login_attempt import LoginAttempt
    from repositories.login_attempt_repository import (
        LoginAttemptRepository
    )

    now = datetime.now(
        UTC
    )

    attempts = [
        LoginAttempt(
            username="user-a",
            ip_address="10.0.0.1",
            failed_at=now - timedelta(minutes=1),
            created_at=now - timedelta(minutes=1)
        ),
        LoginAttempt(
            username="user-a",
            ip_address="10.0.0.2",
            failed_at=now - timedelta(minutes=2),
            created_at=now - timedelta(minutes=2)
        ),
        LoginAttempt(
            username="user-b",
            ip_address="10.0.0.1",
            failed_at=now - timedelta(minutes=3),
            created_at=now - timedelta(minutes=3)
        ),
    ]

    db.add_all(attempts)
    db.commit()

    repository = LoginAttemptRepository(
        db
    )

    result = repository.get_recent_failed_attempts(
        username="user-a",
        ip_address="10.0.0.1",
        since=now - timedelta(minutes=10)
    )

    assert len(result) == 1
    assert result[0].username == "user-a"
    assert result[0].ip_address == "10.0.0.1"
    
# =========================================================
# FILTER USERNAME TANPA IP
# =========================================================

def test_get_recent_failed_attempts_username_only(
    db
):
    from datetime import datetime, timedelta, UTC

    from models.login_attempt import LoginAttempt
    from repositories.login_attempt_repository import (
        LoginAttemptRepository
    )

    now = datetime.now(
        UTC
    )

    attempts = [
        LoginAttempt(
            username="user-a",
            ip_address="10.0.0.1",
            failed_at=now - timedelta(minutes=1),
            created_at=now - timedelta(minutes=1)
        ),
        LoginAttempt(
            username="user-a",
            ip_address="10.0.0.2",
            failed_at=now - timedelta(minutes=2),
            created_at=now - timedelta(minutes=2)
        ),
        LoginAttempt(
            username="user-b",
            ip_address="10.0.0.1",
            failed_at=now - timedelta(minutes=3),
            created_at=now - timedelta(minutes=3)
        ),
    ]

    db.add_all(attempts)
    db.commit()

    repository = LoginAttemptRepository(
        db
    )

    result = repository.get_recent_failed_attempts(
        username="user-a",
        ip_address=None,
        since=now - timedelta(minutes=10)
    )

    assert len(result) == 2
    assert all(
        attempt.username == "user-a"
        for attempt in result
    )
    
    
# =========================================================
# SINCE - TEPAT PADA BATAS
# =========================================================

def test_get_recent_failed_attempts_includes_exact_since(
    db
):
    from datetime import datetime, timedelta, UTC

    from models.login_attempt import LoginAttempt
    from repositories.login_attempt_repository import (
        LoginAttemptRepository
    )

    now = datetime.now(
        UTC
    )

    since = now - timedelta(
        minutes=10
    )

    attempt = LoginAttempt(
        username="boundary-user",
        ip_address="10.0.0.1",
        failed_at=since,
        created_at=since
    )

    db.add(attempt)
    db.commit()

    repository = LoginAttemptRepository(
        db
    )

    result = repository.get_recent_failed_attempts(
        username="boundary-user",
        ip_address="10.0.0.1",
        since=since
    )

    assert len(result) == 1
    assert result[0].failed_at == since


# =========================================================
# SINCE - SEBELUM BATAS
# =========================================================

def test_get_recent_failed_attempts_excludes_before_since(
    db
):
    from datetime import datetime, timedelta, UTC

    from models.login_attempt import LoginAttempt
    from repositories.login_attempt_repository import (
        LoginAttemptRepository
    )

    now = datetime.now(
        UTC
    )

    since = now - timedelta(
        minutes=10
    )

    attempt = LoginAttempt(
        username="boundary-user",
        ip_address="10.0.0.1",
        failed_at=since - timedelta(
            seconds=1
        ),
        created_at=since - timedelta(
            seconds=1
        )
    )

    db.add(attempt)
    db.commit()

    repository = LoginAttemptRepository(
        db
    )

    result = repository.get_recent_failed_attempts(
        username="boundary-user",
        ip_address="10.0.0.1",
        since=since
    )

    assert result == []
    
# =========================================================
# URUTAN - ATTEMPT TERBARU ADA DI POSISI PERTAMA
# =========================================================

def test_get_recent_failed_attempts_returns_latest_first(
    db
):
    from datetime import (
        datetime,
        timedelta,
        UTC
    )

    from models.login_attempt import LoginAttempt

    from repositories.login_attempt_repository import (
        LoginAttemptRepository
    )

    now = datetime.now(UTC)

    older = LoginAttempt(
        username="order-user",
        ip_address="10.0.0.1",
        failed_at=now - timedelta(minutes=3),
        created_at=now - timedelta(minutes=3)
    )

    latest = LoginAttempt(
        username="order-user",
        ip_address="10.0.0.1",
        failed_at=now - timedelta(minutes=1),
        created_at=now - timedelta(minutes=1)
    )

    middle = LoginAttempt(
        username="order-user",
        ip_address="10.0.0.1",
        failed_at=now - timedelta(minutes=2),
        created_at=now - timedelta(minutes=2)
    )

    db.add_all([
        older,
        latest,
        middle
    ])

    db.commit()

    repository = LoginAttemptRepository(
        db
    )

    result = repository.get_recent_failed_attempts(
        username="order-user",
        ip_address="10.0.0.1",
        since=now - timedelta(minutes=10)
    )

    assert len(result) == 3

    assert result[0].failed_at == latest.failed_at
    assert result[1].failed_at == middle.failed_at
    assert result[2].failed_at == older.failed_at