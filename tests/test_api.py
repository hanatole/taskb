from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api import app
from models import Task

BASE_URL = "http://localhost:8000/api/v1"

client = TestClient(app)


def test_should_return_ok():
    response = client.get(f"{BASE_URL}/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task_with_valide_data_should_succeed(mock_db_session):
    def refresh(obj):
        obj.id = 1

    mock_db_session.refresh = refresh
    payload = {
        "title": "Test task",
        "priority": "LOW",
        "description": "Test task description",
        "dueDate": "2023-01-01",
    }
    response = client.post(f"{BASE_URL}/tasks", json=payload)
    assert response.status_code == 201
    assert response.headers["location"] == f"{BASE_URL}/tasks/1"
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == payload["title"]
    assert data["status"] == "OPEN"
    assert data["description"] == payload["description"]
    assert data["dueDate"] == payload["dueDate"]
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()


@pytest.mark.parametrize(
    "payload,message",
    [
        (None, "body: Body required"),
        (
            {
                "title": "Learn coding",
                "description": "Updated task description",
                "dueDate": "2023-01-01",
            },
            "priority: Field required",
        ),
        (
            {
                "title": "Le",
                "description": "Updated task description",
                "dueDate": "2023-01-01",
                "priority": "LOW",
            },
            "title: String should have at least 3 characters",
        ),
    ],
)
def test_create_task_with_invalid_data_should_fail(payload, message):
    response = client.post(f"{BASE_URL}/tasks", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == message


def test_get_existing_task_should_succeed(mock_db_session):
    mock_db_session.get.return_value = Task(
        id=1,
        title="Test task",
        description="Description",
        status="OPEN",
        priority="LOW",
        due_date="2023-01-01",
    )
    response = client.get(f"{BASE_URL}/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test task"
    assert data["status"] == "OPEN"
    assert data["description"] == "Description"
    assert data["dueDate"] == "2023-01-01"
    assert data["priority"] == "LOW"


def test_get_non_existing_task_should_fail(mock_db_session):
    mock_db_session.get.return_value = None
    response = client.get(f"{BASE_URL}/tasks/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task 1 not found"


def test_delete_existing_task_should_succeed(mock_db_session):
    mock_db_session.get.return_value = Task(
        id=1,
        title="Test task",
        description="Description",
        status="OPEN",
        priority="LOW",
        due_date="2023-01-01",
    )
    response = client.delete(f"{BASE_URL}/tasks/1")
    assert response.status_code == 204
    mock_db_session.delete.assert_called()
    mock_db_session.commit.assert_called()


def test_delete_non_existing_task_should_fail(mock_db_session):
    mock_db_session.get.return_value = None
    response = client.delete(f"{BASE_URL}/tasks/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task 1 not found"


def test_update_existing_task_with_valid_data_should_succeed(mock_db_session):
    mock_db_session.get.return_value = Task(
        id=1,
        title="Test task",
        status="OPEN",
        priority="LOW",
        due_date="2023-01-01",
        description="Description",
    )
    payload = {
        "title": "Learn coding",
        "priority": "HIGH",
        "description": "Updated task description",
        "dueDate": "2023-01-01",
    }
    response = client.put(f"{BASE_URL}/tasks/1", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["title"] == payload["title"]
    assert response.json()["priority"] == payload["priority"]
    assert response.json()["description"] == payload["description"]
    assert response.json()["dueDate"] == payload["dueDate"]
    mock_db_session.commit.assert_called()


def test_update_non_existing_task_should_fail(mock_db_session):
    mock_db_session.get.return_value = None
    payload = {
        "title": "Learn coding",
        "priority": "HIGH",
        "description": "Updated task description",
        "dueDate": "2023-01-01",
    }
    response = client.put(f"{BASE_URL}/tasks/1", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task 1 not found"


@pytest.mark.parametrize(
    "payload,message",
    [
        (None, "body: Body required"),
        (
            {"title": "Learn coding", "priority": "HIGH", "description": "Description"},
            "dueDate: Field required",
        ),
        (
            {"title": "Learn coding", "priority": "URGENT", "dueDate": "2023-01-01"},
            "priority: Input should be 'LOW', 'MEDIUM' or 'HIGH'",
        ),
    ],
)
def test_update_existing_task_with_invalid_data_should_fail(payload, message):
    response = client.put(f"{BASE_URL}/tasks/1", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == message


def test_get_all_no_filters(mock_db_session, fake_page):
    with patch("api.paginate", return_value=fake_page) as mock_paginate:
        response = client.get(f"{BASE_URL}/tasks")

        assert response.status_code == 200
        assert response.json() == fake_page
        mock_paginate.assert_called_once()
        args, kwargs = mock_paginate.call_args
        assert args[0] == mock_db_session


def test_get_all_with_status_filter(mock_db_session, fake_page):
    with patch("api.paginate", return_value=fake_page) as mock_paginate:
        response = client.get(f"{BASE_URL}/tasks?status=OPEN")

        assert response.status_code == 200
        compiled = str(mock_paginate.call_args[0][1])
        assert "status" in compiled
        assert "= :status_1" in compiled


def test_get_all_with_due_date_filter(mock_db_session, fake_page):
    with patch("api.paginate", return_value=fake_page) as mock_paginate:
        response = client.get(f"{BASE_URL}/tasks?due_date=TODAY")

        assert response.status_code == 200
        compiled = str(mock_paginate.call_args[0][1])
        assert "due_date" in compiled
        assert "= :due_date_1" in compiled


def test_get_all_with_many_filters(mock_db_session, fake_page):
    with patch("api.paginate", return_value=fake_page) as mock_paginate:
        response = client.get(
            f"{BASE_URL}/tasks?due_date=TODAY&status=OPEN&priority=LOW"
        )

        assert response.status_code == 200
        compiled = str(mock_paginate.call_args[0][1])
        assert all(
            filter(
                lambda x: x in compiled,
                [
                    "status",
                    "= :status_1",
                    "due_date",
                    "= :due_date_1",
                    "priority",
                    "= :priority_1",
                ],
            )
        )


def test_complete_existing_task_should_succeed(mock_db_session):
    mock_db_session.get.return_value = Task(
        id=1,
        title="Learn coding",
        status="OPEN",
        priority="LOW",
        due_date="2023-01-02",
        description="Description",
    )
    response = client.post(f"{BASE_URL}/tasks/1")
    assert response.status_code == 200
    response_payload = response.json()
    assert response_payload["id"] == 1
    assert response_payload["title"] == "Learn coding"
    assert response_payload["status"] == "COMPLETED"
    assert response_payload["priority"] == "LOW"
    assert response_payload["description"] == "Description"
    mock_db_session.commit.assert_called()


def test_complete_non_existing_task_should_fail(mock_db_session):
    mock_db_session.get.return_value = None
    response = client.post(f"{BASE_URL}/tasks/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task 1 not found"
