import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

initial_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_participant(client):
    email = "test.user@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup?email=test.user%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test.user@mergington.edu for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    email = "duplicate@mergington.edu"
    client.post(f"/activities/Chess%20Club/signup?email={email}")
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown%20Club/signup?email=someone%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_removes_participant(client):
    email = "delete.test@mergington.edu"
    client.post(f"/activities/Chess%20Club/signup?email={email}")

    response = client.delete(
        f"/activities/Chess%20Club/participants?email={email}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_delete_missing_participant_returns_404(client):
    email = "missing@mergington.edu"

    response = client.delete(
        f"/activities/Chess%20Club/participants?email={email}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
