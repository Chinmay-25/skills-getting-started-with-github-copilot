import pytest
import time
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # Since FastAPI's StaticFiles mount directly serves the file, we don't check for redirect

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_signup_activity_success():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_activity_full():
    # First, fill up an activity
    activity_name = "Chess Club"
    activities_response = client.get("/activities")
    activities = activities_response.json()
    max_participants = activities[activity_name]["max_participants"]
    
    # Add participants until full
    for i in range(max_participants):
        email = f"test{i}@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Try to add one more
    response = client.post(f"/activities/{activity_name}/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_activity_success():
    # Use "Art Club" as it has more space for new participants
    activity_name = "Art Club"
    email = "unregister_test_new@mergington.edu"
    
    # Sign up the participant
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200  # Ensure signup succeeded
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]
    
    # Then unregister them
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_activity_not_found():
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_activity_not_registered():
    response = client.post("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "Student is not registered" in response.json()["detail"]