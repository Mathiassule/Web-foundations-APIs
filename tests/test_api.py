import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import academic_service

client = TestClient(app)

AUTH_HEADER = {"Authorization": "Basic YWRtaW46YWRtaW4xMjM="}  # admin:admin123


@pytest.fixture(autouse=True)
def reset_service():
    """Reset the service internal state before each test run."""
    academic_service._subjects.clear()
    academic_service._assessments.clear()
    academic_service._scores.clear()


def test_root_health():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "operational"


def test_auth_rejection():
    # Attempting to create subject without auth header
    res = client.post("/subjects", json={"id": "CSC101", "name": "Computer Science", "credit_units": 3})
    assert res.status_code == 401
    assert "detail" in res.json()


def test_create_and_list_subject():
    res = client.post(
        "/subjects",
        json={"id": "CSC101", "name": "Intro to Computer Science", "credit_units": 3},
        headers=AUTH_HEADER
    )
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == "CSC101"

    # Duplicate creation error
    res_dup = client.post(
        "/subjects",
        json={"id": "CSC101", "name": "Duplicate CS", "credit_units": 3},
        headers=AUTH_HEADER
    )
    assert res_dup.status_code == 400

    # List subjects
    res_list = client.get("/subjects")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1


def test_assessment_flow():
    # Setup subject
    client.post("/subjects", json={"id": "MTH101", "name": "Calculus I", "credit_units": 4}, headers=AUTH_HEADER)

    # Create assessment
    res = client.post(
        "/assessments",
        json={
            "id": "MTH-QUIZ1",
            "subject_id": "MTH101",
            "title": "Quiz 1: Limits",
            "max_score": 20.0,
            "weight_percentage": 10.0
        },
        headers=AUTH_HEADER
    )
    assert res.status_code == 201
    assert res.json()["max_score"] == 20.0

    # Assessment for nonexistent subject fails
    res_fail = client.post(
        "/assessments",
        json={
            "id": "BIO-QUIZ1",
            "subject_id": "BIO101",
            "title": "Quiz on Cells",
            "max_score": 20.0,
            "weight_percentage": 10.0
        },
        headers=AUTH_HEADER
    )
    assert res_fail.status_code == 404


def test_score_and_average_calculation():
    # Setup
    client.post("/subjects", json={"id": "PHY101", "name": "Physics I", "credit_units": 3}, headers=AUTH_HEADER)
    client.post(
        "/assessments",
        json={"id": "PHY-EXAM", "subject_id": "PHY101", "title": "Final Exam", "max_score": 100.0, "weight_percentage": 60.0},
        headers=AUTH_HEADER
    )

    # Score exceeding maximum validation check
    res_invalid = client.post(
        "/scores",
        json={"student_id": "STD202601", "assessment_id": "PHY-EXAM", "obtained_score": 110.0},
        headers=AUTH_HEADER
    )
    assert res_invalid.status_code == 400

    # Record valid score
    res_score = client.post(
        "/scores",
        json={"student_id": "STD202601", "assessment_id": "PHY-EXAM", "obtained_score": 85.0},
        headers=AUTH_HEADER
    )
    assert res_score.status_code == 201
    score_id = res_score.json()["id"]
    assert res_score.json()["grade"] == "B"

    # Update score
    res_update = client.put(f"/scores/{score_id}", json={"obtained_score": 95.0}, headers=AUTH_HEADER)
    assert res_update.status_code == 200
    assert res_update.json()["grade"] == "A"
    assert res_update.json()["percentage"] == 95.0

    # Retrieve student results
    res_student = client.get("/students/STD202601/results")
    assert res_student.status_code == 200
    student_data = res_student.json()
    assert student_data["overall_average"] == 95.0
    assert len(student_data["scores"]) == 1

    # Subject average
    res_subj_avg = client.get("/subjects/PHY101/average")
    assert res_subj_avg.status_code == 200
    assert res_subj_avg.json()["average_percentage"] == 95.0
