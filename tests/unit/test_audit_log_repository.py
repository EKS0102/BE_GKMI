from unittest.mock import MagicMock

from models.audit_log import AuditLog
from repositories.audit_log_repository import AuditLogRepository


def test_add():
    db = MagicMock()
    repository = AuditLogRepository(db)

    audit_log = MagicMock(spec=AuditLog)

    repository.add(audit_log)

    db.add.assert_called_once_with(audit_log)


def test_get_by_id():
    db = MagicMock()
    repository = AuditLogRepository(db)

    query = db.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = "audit-log-result"

    result = repository.get_by_id(10)

    db.query.assert_called_once_with(AuditLog)
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once_with()

    assert result == "audit-log-result"


def test_get_by_user():
    db = MagicMock()
    repository = AuditLogRepository(db)

    query = db.query.return_value
    filtered_query = query.filter.return_value
    ordered_query = filtered_query.order_by.return_value
    ordered_query.all.return_value = [
        "audit-log-1",
        "audit-log-2",
    ]

    result = repository.get_by_user(10)

    db.query.assert_called_once_with(AuditLog)
    query.filter.assert_called_once()
    filtered_query.order_by.assert_called_once()
    ordered_query.all.assert_called_once_with()

    assert result == [
        "audit-log-1",
        "audit-log-2",
    ]


def test_refresh():
    db = MagicMock()
    repository = AuditLogRepository(db)

    audit_log = MagicMock(spec=AuditLog)

    repository.refresh(audit_log)

    db.refresh.assert_called_once_with(audit_log)