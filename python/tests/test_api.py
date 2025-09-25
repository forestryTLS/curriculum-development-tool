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
    assert "An error occurred while processing the request." == json_response["message"]
        
def test_invalid_file_type_create_course_from_syllabi():
    body = {
        "file_path": "tests/data/badFileExample.pdf",
        "client_original_filename": "badFileExample.pdf"
    }
    response = client.post("/create_course_from_syllabi", json=body)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "error"
    assert "An error occurred while processing the request." == json_response["message"]
    

def test_valid_file_create_course_from_syllabi():
    body = {
        "file_path": "tests/data/syllabi/TEST101_2025W1_PDF_Tabular_Assessments.pdf",
        "client_original_filename": "TEST101_2025W1_PDF_Tabular_Assessments.pdf"
    }
    response = client.post("/create_course_from_syllabi", json=body)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert "Course created successfully" == json_response["message"]
    data = json_response["data"]
    assert data['code'] == 'TEST'
    assert data['number'] == 101
    assert data['term'] == 'W1'
    assert data['year'] == 2025
    assert data['title'] == 'TEST Course Syllabus' 
    assert data['level'] == 'Undergraduate'
    assert data['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus.'
    assert data['goals'] == ['Explain the core concepts, theories, and terminology related to [subject area].', 
                                        'Apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].', 
                                        'Evaluate and critique information or arguments using evidence-based reasoning.', 
                                        'Communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.', 
                                        'Explore the connections between theoretical knowledge and real-world practice.', 
                                        'Integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert data['assessments'] == [['Test Assignments', 27], 
                                   ['Test participation', 3], 
                                   ['Test Midterm', 40], 
                                   ['Test Individual final Exam', 30]]