"""
Tests for the Mergington High School Activities API

Tests cover the main endpoints for viewing activities, signing up,
and unregistering from extracurricular activities.
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


# Baseline activities state for test isolation
BASELINE_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for interschool tournaments",
        "schedule": "Mondays, Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis skills and participate in matches",
        "schedule": "Tuesdays, Thursdays, 3:45 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["sarah@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and sculpture techniques",
        "schedule": "Mondays, Wednesdays, 3:30 PM - 4:45 PM",
        "max_participants": 18,
        "participants": ["maya@mergington.edu", "lucas@mergington.edu"]
    },
    "Theater Club": {
        "description": "Acting, stage production, and performing arts",
        "schedule": "Thursdays, Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["alex@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Design, build, and program robots for competitions",
        "schedule": "Tuesdays, Thursdays, 4:30 PM - 6:00 PM",
        "max_participants": 16,
        "participants": ["ryan@mergington.edu", "nina@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Mondays, Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["jordan@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app with fresh activities state"""
    # Reset activities to baseline before each test with deep copy
    activities.clear()
    baseline_copy = copy.deepcopy(BASELINE_ACTIVITIES)
    activities.update(baseline_copy)
    
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing required fields"
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"

    def test_chess_club_has_baseline_participants(self, client):
        """Test that Chess Club has the expected baseline participants"""
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_successfully(self, client):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_increases_participant_count(self, client):
        """Test that signup increases the participant count"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Sign up new participant
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Verify count increased
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count + 1

    def test_signup_adds_participant_to_list(self, client):
        """Test that signup adds participant to the activity's participant list"""
        email = "newstudent@mergington.edu"
        
        # Sign up participant
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Verify participant appears in list
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert email in participants

    def test_signup_second_participant(self, client):
        """Test signing up a second new participant to same activity"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Sign up first participant
        response1 = client.post(f"/activities/Tennis Club/signup?email={email1}")
        assert response1.status_code == 200
        
        # Sign up second participant
        response2 = client.post(f"/activities/Tennis Club/signup?email={email2}")
        assert response2.status_code == 200
        
        # Verify both are in list
        response = client.get("/activities")
        participants = response.json()["Tennis Club"]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_successfully(self, client):
        """Test successfully unregistering an existing participant"""
        email = "michael@mergington.edu"
        response = client.post(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_removes_participant_from_list(self, client):
        """Test that unregister removes participant from the activity's list"""
        email = "michael@mergington.edu"
        
        # Verify participant is in list before unregister
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister participant
        client.post(f"/activities/Chess Club/unregister?email={email}")
        
        # Verify participant is no longer in list
        response = client.get("/activities")
        assert email not in response.json()["Chess Club"]["participants"]

    def test_unregister_decreases_participant_count(self, client):
        """Test that unregister decreases the participant count"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Unregister a participant
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        # Verify count decreased
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1

    def test_unregister_keeps_other_participants(self, client):
        """Test that unregistering one participant doesn't affect others"""
        # Get initial participants
        response = client.get("/activities")
        initial_participants = response.json()["Chess Club"]["participants"].copy()
        
        # Unregister michael@mergington.edu
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        # Verify other participants are still there
        response = client.get("/activities")
        remaining_participants = response.json()["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in remaining_participants
        assert len(remaining_participants) == len(initial_participants) - 1
