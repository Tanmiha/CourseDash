import sys
import os
import json
import pytest

# Add parent directory to sys.path so 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, DATA_FILE


@pytest.fixture
def client():
    app.config['TESTING'] = True
    
    # Initialize clean test data
    sample_courses = [
        {
            'id': 1,
            'name': 'Test Course 1',
            'description': 'Description 1',
            'target_date': '2026-12-31',
            'status': 'In Progress',
            'created_at': '2026-01-01 10:00:00'
        }
    ]
    with open(DATA_FILE, 'w') as f:
        json.dump(sample_courses, f)

    with app.test_client() as client:
        yield client


def test_get_all_courses(client):
    response = client.get('/api/courses')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['courses']) >= 1


def test_get_statistics(client):
    response = client.get('/api/courses/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'statistics' in data


def test_add_course_validation(client):
    # Test missing required field
    invalid_payload = {
        'name': 'Incomplete Course'
    }
    response = client.post('/api/courses', json=invalid_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False