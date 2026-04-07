from unittest.mock import MagicMock

import pytest

from api import app, get_session

session_mock = MagicMock()


def override_get_session():
    yield session_mock


@pytest.fixture
def mock_db_session():
    yield session_mock


@pytest.fixture
def fake_page():
    return {"items": [], "total": 0, "page": 1, "size": 5, "pages": 1}


app.dependency_overrides[get_session] = override_get_session
