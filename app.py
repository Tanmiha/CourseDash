"""
MyLearnTracker - Personal Learning Goal Tracker API
A simple REST API to track courses you want to learn
"""

from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime

# Initialize Flask to automatically locate templates/ and static/ folders
app = Flask(__name__)
CORS(app)  # Enable CORS so browser frontends can call this API

# Configuration
DATA_FILE = 'courses.json'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_courses():
    """
    Load courses from the JSON file.
    If file doesn't exist, create an empty one.
    """
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
        return []
    
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_courses(courses):
    """
    Save courses to the JSON file.
    """
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(courses, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving courses: {e}")
        return False


def get_next_id(courses):
    """
    Generate the next available ID for a new course.
    """
    if not courses:
        return 1
    return max(course['id'] for course in courses) + 1


def find_course_by_id(courses, course_id):
    """
    Find a course by its ID.
    Returns the course and its index, or (None, -1) if not found.
    """
    for index, course in enumerate(courses):
        if course['id'] == course_id:
            return course, index
    return None, -1


def validate_course_data(data, required_fields):
    """
    Validate that required fields are present in the data.
    Returns (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    valid_statuses = ['Not Started', 'In Progress', 'Completed']
    if 'status' in data and data['status'] not in valid_statuses:
        return False, f"Status must be one of: {', '.join(valid_statuses)}"
    
    if 'target_date' in data and data['target_date']:
        try:
            datetime.strptime(data['target_date'], '%Y-%m-%d')
        except ValueError:
            return False, "target_date must be in YYYY-MM-DD format"
    
    return True, None


# ============================================================================
# FRONTEND & API ROUTES
# ============================================================================

@app.route('/')
def home():
    """
    Serve index.html from templates/ folder
    """
    return render_template('index.html')


@app.route('/<filename>')
def serve_static_root(filename):
    """
    Fallback handler to serve assets directly from static/ when requested at root path
    """
    static_file_path = os.path.join(app.root_path, 'static', filename)
    if os.path.exists(static_file_path):
        return send_from_directory('static', filename)
    return jsonify({'success': False, 'error': 'File not found'}), 404


@app.route('/api')
def api_info():
    """
    API Information Endpoint
    """
    return jsonify({
        'message': 'Welcome to MyLearnTracker API!',
        'version': '1.0',
        'endpoints': {
            'GET /api/courses': 'Get all courses',
            'GET /api/courses/<id>': 'Get a specific course',
            'POST /api/courses': 'Add a new course',
            'PUT /api/courses/<id>': 'Update a course',
            'DELETE /api/courses/<id>': 'Delete a course',
            'GET /api/courses/stats': 'Get course completion statistics',
            'GET /api/courses/search?q=query': 'Search courses'
        }
    })


@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    try:
        courses = load_courses()
        return jsonify({
            'success': True,
            'count': len(courses),
            'courses': courses
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve courses: {str(e)}'
        }), 500


@app.route('/api/courses/stats', methods=['GET'])
def get_statistics():
    try:
        courses = load_courses()
        
        stats = {
            'total_courses': len(courses),
            'not_started': len([c for c in courses if c.get('status') == 'Not Started']),
            'in_progress': len([c for c in courses if c.get('status') == 'In Progress']),
            'completed': len([c for c in courses if c.get('status') == 'Completed'])
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get statistics: {str(e)}'
        }), 500


@app.route('/api/courses/search', methods=['GET'])
def search_courses():
    try:
        search_query = request.args.get('q', '').lower()
        
        if not search_query:
            return jsonify({
                'success': False,
                'error': 'Search query parameter "q" is required'
            }), 400
        
        courses = load_courses()
        results = [
            course for course in courses
            if search_query in course.get('name', '').lower() or 
               search_query in course.get('description', '').lower()
        ]
        
        return jsonify({
            'success': True,
            'count': len(results),
            'courses': results
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to search courses: {str(e)}'
        }), 500


@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    try:
        courses = load_courses()
        course, _ = find_course_by_id(courses, course_id)
        
        if course:
            return jsonify({
                'success': True,
                'course': course
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Course with ID {course_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve course: {str(e)}'
        }), 500


@app.route('/api/courses', methods=['POST'])
def add_course():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        required_fields = ['name', 'description', 'target_date', 'status']
        is_valid, error_message = validate_course_data(data, required_fields)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400
        
        courses = load_courses()
        
        new_course = {
            'id': get_next_id(courses),
            'name': data['name'],
            'description': data['description'],
            'target_date': data['target_date'],
            'status': data['status'],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        courses.append(new_course)
        
        if save_courses(courses):
            return jsonify({
                'success': True,
                'message': 'Course added successfully',
                'course': new_course
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save course'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to add course: {str(e)}'
        }), 500


@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        courses = load_courses()
        course, index = find_course_by_id(courses, course_id)
        
        if not course:
            return jsonify({
                'success': False,
                'error': f'Course with ID {course_id} not found'
            }), 404
        
        is_valid, error_message = validate_course_data(data, [])
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400
        
        if 'name' in data:
            course['name'] = data['name']
        if 'description' in data:
            course['description'] = data['description']
        if 'target_date' in data:
            course['target_date'] = data['target_date']
        if 'status' in data:
            course['status'] = data['status']
        
        courses[index] = course
        
        if save_courses(courses):
            return jsonify({
                'success': True,
                'message': 'Course updated successfully',
                'course': course
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save changes'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update course: {str(e)}'
        }), 500


@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        courses = load_courses()
        course, index = find_course_by_id(courses, course_id)
        
        if not course:
            return jsonify({
                'success': False,
                'error': f'Course with ID {course_id} not found'
            }), 404
        
        deleted_course = courses.pop(index)
        
        if save_courses(courses):
            return jsonify({
                'success': True,
                'message': 'Course deleted successfully',
                'deleted_course': deleted_course
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save changes'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete course: {str(e)}'
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ============================================================================
# RUN THE APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("MyLearnTracker API is starting...")
    print("=" * 60)
    print(f"Data will be stored in: {os.path.abspath(DATA_FILE)}")
    print("API will be available at: http://localhost:5000")
    print("=" * 60)
    print("\nPress CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)