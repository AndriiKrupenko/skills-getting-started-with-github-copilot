import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity():
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=test@example.com"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Verify participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]


def test_signup_duplicate():
    """Test signing up for the same activity twice"""
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")

    # Second signup should fail
    response = client.post(
        "/activities/Chess%20Club/signup?email=duplicate@example.com"
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/NonExistent%20Activity/signup?email=test@example.com"
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_remove_participant():
    """Test removing a participant from an activity"""
    # First add a participant
    client.post("/activities/Tennis%20Club/signup?email=remove@example.com")

    # Then remove them
    response = client.delete(
        "/activities/Tennis%20Club/participants/remove@example.com"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Removed remove@example.com from Tennis Club" in data["message"]

    # Verify participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "remove@example.com" not in data["Tennis Club"]["participants"]


def test_remove_nonexistent_participant():
    """Test removing a participant who is not signed up"""
    response = client.delete(
        "/activities/Chess%20Club/participants/nonexistent@example.com"
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]


def test_remove_from_nonexistent_activity():
    """Test removing from a non-existent activity"""
    response = client.delete(
        "/activities/NonExistent%20Activity/participants/test@example.com"
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    """Test that root endpoint redirects to static HTML"""
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers.get("location", "")