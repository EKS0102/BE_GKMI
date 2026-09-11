from unittest.mock import Mock

import pytest

from unit_of_work import UnitOfWork


# =========================================================
# CONTEXT MANAGER - COMMIT
# =========================================================

def test_unit_of_work_context_manager_commit():
    session = Mock()

    with UnitOfWork(session) as uow:
        assert uow.session is session

    session.commit.assert_called_once()
    session.rollback.assert_not_called()


# =========================================================
# CONTEXT MANAGER - ROLLBACK
# =========================================================

def test_unit_of_work_context_manager_rollback():
    session = Mock()

    with pytest.raises(
        RuntimeError,
        match="test error"
    ):
        with UnitOfWork(session):
            raise RuntimeError(
                "test error"
            )

    session.rollback.assert_called_once()
    session.commit.assert_not_called()