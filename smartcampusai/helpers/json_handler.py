import os
import json
import logging
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# File locks to prevent concurrent write issues in Streamlit
_locks = {}
_lock_access = Lock()

def _get_lock(filename: str) -> Lock:
    with _lock_access:
        if filename not in _locks:
            _locks[filename] = Lock()
        return _locks[filename]

# Define base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Required DB files with rich initial mock data
DB_FILES = {
    "users.json": [
        {"name": "Campus Admin", "email": "admin@smartcampus.edu", "mobile": "9999999999", "username": "admin", "password": "$2b$12$nSoW9WTfsm8Pi20LthhfheEPhip9p7wRI6cOD1npPE/l0hlbUZy1y", "role": "Admin"},
        {"name": "Dr. Sarah Connor", "email": "sconnor@smartcampus.edu", "mobile": "9888888888", "username": "faculty", "password": "$2b$12$jNJWYWl0RiD3iC67EshTeORsB.FX/cOcZTDYtoN8By0QXA4sdEhvS", "role": "Faculty"},
        {"name": "John Connor", "email": "jconnor@smartcampus.edu", "mobile": "9777777777", "username": "student", "password": "$2b$12$CHSc7zBK6GMg/n.st.DC.uJaCu5UQce1DzMWmB7X0vXomQU.gmFve", "role": "Student"}
    ],
    "students.json": [
        {"student_id": "STU101", "name": "John Connor", "branch": "CSE", "year": "3rd Year", "section": "A", "phone": "9777777777", "email": "jconnor@smartcampus.edu", "address": "123 Resistance Way, LA", "skills": "Python, CyberSecurity, Hardware hacks"},
        {"student_id": "STU102", "name": "Marcus Wright", "branch": "ECE", "year": "4th Year", "section": "B", "phone": "9887776665", "email": "mwright@smartcampus.edu", "address": "456 Cyberdyne Blvd, SF", "skills": "C++, Robotics, Signal Processing"},
        {"student_id": "STU103", "name": "Kate Brewster", "branch": "Civil", "year": "2nd Year", "section": "A", "phone": "9555554433", "email": "kbrewster@smartcampus.edu", "address": "789 Bunker Hill, TX", "skills": "AutoCAD, Structural Design, Project Mgmt"}
    ],
    "attendance.json": [
        {"date": "2026-07-10", "student_id": "STU101", "name": "John Connor", "branch": "CSE", "year": "3rd Year", "section": "A", "status": "Present"},
        {"date": "2026-07-10", "student_id": "STU102", "name": "Marcus Wright", "branch": "ECE", "year": "4th Year", "section": "B", "status": "Present"},
        {"date": "2026-07-10", "student_id": "STU103", "name": "Kate Brewster", "branch": "Civil", "year": "2nd Year", "section": "A", "status": "Absent"},
        {"date": "2026-07-11", "student_id": "STU101", "name": "John Connor", "branch": "CSE", "year": "3rd Year", "section": "A", "status": "Present"},
        {"date": "2026-07-11", "student_id": "STU102", "name": "Marcus Wright", "branch": "ECE", "year": "4th Year", "section": "B", "status": "Late"},
        {"date": "2026-07-11", "student_id": "STU103", "name": "Kate Brewster", "branch": "Civil", "year": "2nd Year", "section": "A", "status": "Present"},
        {"date": "2026-07-12", "student_id": "STU101", "name": "John Connor", "branch": "CSE", "year": "3rd Year", "section": "A", "status": "Present"},
        {"date": "2026-07-12", "student_id": "STU102", "name": "Marcus Wright", "branch": "ECE", "year": "4th Year", "section": "B", "status": "Present"},
        {"date": "2026-07-12", "student_id": "STU103", "name": "Kate Brewster", "branch": "Civil", "year": "2nd Year", "section": "A", "status": "Present"},
        {"date": "2026-07-13", "student_id": "STU101", "name": "John Connor", "branch": "CSE", "year": "3rd Year", "section": "A", "status": "Present"},
        {"date": "2026-07-13", "student_id": "STU102", "name": "Marcus Wright", "branch": "ECE", "year": "4th Year", "section": "B", "status": "Absent"},
        {"date": "2026-07-13", "student_id": "STU103", "name": "Kate Brewster", "branch": "Civil", "year": "2nd Year", "section": "A", "status": "Present"}
    ],
    "placements.json": [
        {"company_name": "Google", "package": "32 LPA", "eligible_branches": ["CSE", "ECE"], "drive_date": "2026-08-15", "applied_students": ["STU101"], "selected_students": ["STU101"]},
        {"company_name": "Microsoft", "package": "28 LPA", "eligible_branches": ["CSE"], "drive_date": "2026-09-02", "applied_students": ["STU101", "STU102"], "selected_students": []},
        {"company_name": "Infosys", "package": "6.5 LPA", "eligible_branches": ["CSE", "ECE", "Civil"], "drive_date": "2026-09-10", "applied_students": ["STU103"], "selected_students": ["STU103"]}
    ],
    "announcements.json": [
        {"id": "ann_1", "title": "Google Recruitment Drive", "content": "Google campus recruitment drive is scheduled for August 15, 2026. Eligible branches: CSE and ECE. Register on the Placements page before August 10.", "author": "Campus Admin", "date": "2026-07-14"},
        {"id": "ann_2", "title": "Semester Registration Deadline", "content": "Please complete your course and semester registrations on or before July 25, 2026. Late fees will apply after the deadline.", "author": "Dr. Sarah Connor", "date": "2026-07-12"}
    ],
    "events.json": [
        {"id": "evt_1", "title": "TechFest 2026", "date": "2026-08-01", "time": "09:00 AM", "venue": "Main Auditorium", "description": "Annual technical symposium of SmartCampusAI. Hackathons, paper presentations, and robotic workshops."},
        {"id": "evt_2", "title": "AI & Ethics Guest Lecture", "date": "2026-07-20", "time": "02:30 PM", "venue": "Seminar Hall-A", "description": "Distinguished lecture on the challenges and future of AI ethics in education and corporate domains."}
    ],
    "chat_history.json": []
}

def init_db():
    """Create all required JSON files with initial structures if they do not exist."""
    for filename, default_val in DB_FILES.items():
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(default_val, f, indent=4)
                logger.info(f"Initialized empty JSON database: {filename}")
            except Exception as e:
                logger.error(f"Failed to initialize JSON database {filename}: {str(e)}")

# Initialize database right away on import
init_db()

def _get_path(filename: str) -> str:
    """Return the absolute path for a database file."""
    return os.path.join(DATA_DIR, filename)

def load_json(filename: str) -> list:
    """Load and return the list of items in the JSON database file."""
    file_path = _get_path(filename)
    lock = _get_lock(filename)
    
    with lock:
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            logger.error(f"JSON decode error in {filename}. Database may be corrupted. Returning empty list.")
            return []
        except Exception as e:
            logger.error(f"Error loading JSON database {filename}: {str(e)}")
            return []

def save_json(filename: str, data: list) -> bool:
    """Overwrite the database file with new data."""
    file_path = _get_path(filename)
    lock = _get_lock(filename)
    
    with lock:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON database {filename}: {str(e)}")
            return False

def append_json(filename: str, item: dict) -> bool:
    """Append a single record to the database file."""
    data = load_json(filename)
    data.append(item)
    return save_json(filename, data)

def update_json(filename: str, match_key: str, match_value: str, updated_fields: dict) -> bool:
    """Find a record matching a key/value pair and update specified fields."""
    data = load_json(filename)
    found = False
    for item in data:
        if str(item.get(match_key)) == str(match_value):
            item.update(updated_fields)
            found = True
            
    if found:
        return save_json(filename, data)
    logger.warning(f"Record with {match_key}={match_value} not found in {filename} to update.")
    return False

def delete_json(filename: str, match_key: str, match_value: str) -> bool:
    """Delete record(s) matching a key/value pair."""
    data = load_json(filename)
    initial_length = len(data)
    filtered_data = [item for item in data if str(item.get(match_key)) != str(match_value)]
    
    if len(filtered_data) < initial_length:
        return save_json(filename, filtered_data)
    logger.warning(f"Record with {match_key}={match_value} not found in {filename} to delete.")
    return False
