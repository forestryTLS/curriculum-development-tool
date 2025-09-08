from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_non_post_request_create_course_from_syllabi():
    response = client.get("/create_course_from_syllabi")
    assert response.status_code == 405 
    
def test_missing_post_body_create_course_from_syllabi():
    response = client.post("/create_course_from_syllabi")
    assert response.status_code == 422
    
def test_incomplete_post_body_create_course_from_syllabi():
    body = {
        "client_original_filename": "syllabus.pdf"
    }
    response = client.post("/create_course_from_syllabi", json=body)
    assert response.status_code == 422

def test_invalid_data_type_post_body_create_course_from_syllabi():
    body = {
        "file_path": 12345,
        "client_original_filename": "syllabus.pdf"
    }
    response = client.post("/create_course_from_syllabi", json=body)
    assert response.status_code == 422
    
def test_invalid_file_path_create_course_from_syllabi():
    body = {
        "file_path": "/invalid/path/to/syllabus.pdf",
        "client_original_filename": "syllabus.pdf"
    }
    response = client.post("/create_course_from_syllabi", json=body)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "error"
    assert "no such file" in json_response["message"]
    
def test_invalid_file_type_create_course_from_syllabi():
    body = {
        "file_path": "tests/data/badFileExample.pdf",
        "client_original_filename": "badFileExample.pdf"
    }
    response = client.post("/create_course_from_syllabi", json=body)
    print(response.json())
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "error"
    assert "Failed to open file" in json_response["message"]