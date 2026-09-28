# CourseDash 🎓

**CourseDash** is a full-stack RESTful Learning Management & Tracking Platform designed to help users track, manage, and complete learning goals cleanly and efficiently.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.11, Flask, Flask-CORS
* **Frontend:** Vanilla JavaScript, HTML5, CSS3
* **Data Storage:** JSON File-based persistence (`courses.json`)
* **Testing & Quality:** Pytest, Flake8
* **CI/CD:** GitHub Actions

---

## 📁 Project Structure

```text
CourseDash/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions CI/CD Pipeline
├── static/
│   ├── styles.css             # Frontend UI styling
│   └── script.js              # Interactivity & fetch calls
├── templates/
│   └── index.html             # Application dashboard UI
├── tests/
│   └── test_app.py            # Automated API unit tests
├── app.py                     # Flask backend REST API
├── courses.json               # Local JSON data store
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation

---

🚀 Getting Started
1. Prerequisites
Ensure you have Python 3.11+ installed on your system.

2. Installation
Clone the repository and set up a virtual environment:
# Navigate to project directory
cd CourseDash

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

3. Run Application Locally
Start the Flask development server:

python app.py

Open your browser and navigate to:
http://localhost:5000

🧪 Testing & Linting
Run automated unit tests and linter checks locally:

# Run pytest test suite
python -m pytest -v

# Run Flake8 linter
flake8 . --max-line-length=100 --exclude=venv,.venv

Method    Endpoint,                    Description
 GET        /                             Serves Frontend UI Dashboard
 GET        /api/courses                  Retrieve all courses
 GET        /api/courses/<id>             Retrieve a specific course by ID
 GET        /api/courses/stats            Retrieve completion statistics
 GET        /api/courses/search?q=query   Search courses by name/description
 POST       /api/courses                  Create a new course
 PUT        /api/courses/<id>             Update an existing course
 DELETE     /api/courses/<id>             Remove a course


🔄 CI/CD Pipeline
Automated checks are configured via GitHub Actions in .github/workflows/ci-cd.yml. On every push or pull_request to the main branch:

Sets up Python 3.11 environment.

Installs required dependencies.

Runs flake8 static code analysis.

Executes the pytest suite for automated verification.




