import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

import src.app as app_module

client = TestClient(app_module.app)

# Keep a pristine copy of the initial activities to reset between tests
INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities before each test
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)
    yield


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    # Expect some known activities and participant lists
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_remove_participant():
    activity = "Art Studio"
    email = "student@example.com"

    # Sign up
    res = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert res.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

    # Remove participant
    res = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})
    assert res.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_duplicate_signup_returns_400():
    activity = "Tennis Club"
    email = "jordan@mergington.edu"  # already in initial list

    res = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert res.status_code == 400


def test_remove_nonexistent_participant_returns_404():
    activity = "Tennis Club"
    email = "nobody@example.com"

    res = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})
    assert res.status_code == 404


def test_signup_nonexistent_activity_returns_404():
    activity = "Not A Club"
    email = "a@example.com"

    res = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert res.status_code == 404
