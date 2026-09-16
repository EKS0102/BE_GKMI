from unittest.mock import MagicMock, patch

from dependencies import (
    get_db,
    get_jemaat_service,
    get_auth_service,
    get_security_cleanup_service,
)


# =========================================================
# GET DB
# =========================================================

def test_get_db_closes_session():

    mock_db = MagicMock()

    with patch(
        "dependencies.SessionLocal",
        return_value=mock_db
    ):

        generator = get_db()

        db = next(generator)

        assert db is mock_db
        mock_db.close.assert_not_called()

        try:
            next(generator)
        except StopIteration:
            pass

        mock_db.close.assert_called_once()


# =========================================================
# JEMAAT SERVICE
# =========================================================

def test_get_jemaat_service():

    mock_db = MagicMock()
    mock_uow = MagicMock()
    mock_service = MagicMock()

    with patch("dependencies.UnitOfWork") as mock_unit_of_work, \
         patch("dependencies.JemaatService") as mock_jemaat_service:

        mock_unit_of_work.return_value = mock_uow
        mock_jemaat_service.return_value = mock_service

        result = get_jemaat_service(mock_db)

    assert result is mock_service

    mock_unit_of_work.assert_called_once_with(mock_db)
    mock_jemaat_service.assert_called_once_with(mock_uow)


# =========================================================
# AUTH SERVICE
# =========================================================

def test_get_auth_service():

    mock_db = MagicMock()
    mock_uow = MagicMock()
    mock_service = MagicMock()

    with patch("dependencies.UnitOfWork") as mock_unit_of_work, \
         patch("dependencies.AuthService") as mock_auth_service:

        mock_unit_of_work.return_value = mock_uow
        mock_auth_service.return_value = mock_service

        result = get_auth_service(mock_db)

    assert result is mock_service

    mock_unit_of_work.assert_called_once_with(mock_db)
    mock_auth_service.assert_called_once_with(mock_uow)


# =========================================================
# SECURITY CLEANUP SERVICE
# =========================================================

def test_get_security_cleanup_service():

    mock_db = MagicMock()
    mock_uow = MagicMock()
    mock_service = MagicMock()

    with patch("dependencies.UnitOfWork") as mock_unit_of_work, \
         patch(
             "dependencies.SecurityCleanupService"
         ) as mock_cleanup_service:

        mock_unit_of_work.return_value = mock_uow
        mock_cleanup_service.return_value = mock_service

        result = get_security_cleanup_service(mock_db)

    assert result is mock_service

    mock_unit_of_work.assert_called_once_with(mock_db)
    mock_cleanup_service.assert_called_once_with(mock_uow)