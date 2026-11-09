
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import requests

app = Flask(__name__)
CORS(app)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_database():
    conn = get_db_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                program TEXT NOT NULL,
                year INTEGER NOT NULL,
                section TEXT NOT NULL,
                source TEXT DEFAULT 'Local'
            )
        """)

        columns = [
            row['name']
            for row in conn.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        ]

        if 'source' not in columns:
            conn.execute("""
                ALTER TABLE students
                ADD COLUMN source TEXT DEFAULT 'Local'
            """)

        conn.commit()

    finally:
        conn.close()


initialize_database()


# ==========================================
# VALIDATE STUDENT DATA
# ==========================================

def validate_student(data):

    if not isinstance(data, dict):
        return None, "Invalid JSON data."

    required_fields = [
        'student_id',
        'name',
        'program',
        'year',
        'section'
    ]

    for field in required_fields:
        if field not in data or str(data[field]).strip() == '':
            return None, f"Missing required field: {field}"

    try:
        year = int(data['year'])
    except (ValueError, TypeError):
        return None, "Year must be a number from 1 to 4."

    if year not in (1, 2, 3, 4):
        return None, "Year must be 1, 2, 3, or 4."

    return {
        'student_id': str(data['student_id']).strip(),
        'name': str(data['name']).strip(),
        'program': str(data['program']).strip(),
        'year': year,
        'section': str(data['section']).strip()
    }, None


# ==========================================
# HOME PAGE
# ==========================================

@app.route('/')
def home():
    return render_template('index.html')


# ==========================================
# STUDENT INFORMATION API
# ==========================================

@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00186",
        "name": "Janine Pagmanoja",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# ==========================================
# GREETING API
# ==========================================

@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student').strip()

    if not name:
        name = 'Student'

    return jsonify({
        "message": f"Hello, {name}!"
    })


# ==========================================
# COURSE INFORMATION API
# ==========================================

@app.route('/course')
def get_course():
    return jsonify({
        "course_code": "IT3120",
        "course_name": "System Integration",
        "units": 3,
        "semester": "First Semester"
    })


# ==========================================
# GRADE CHECKER API
# ==========================================

@app.route('/grade')
def get_grade():
    score = request.args.get('score', type=float)

    if score is None or not 0 <= score <= 100:
        return jsonify({
            "error": "Please provide a score between 0 and 100."
        }), 400

    if score >= 90:
        remark = "Excellent"
    elif score >= 80:
        remark = "Very Good"
    elif score >= 75:
        remark = "Passed"
    else:
        remark = "Failed"

    return jsonify({
        "score": score,
        "remark": remark
    })


# ==========================================
# GET ALL STUDENTS
# ==========================================

@app.route('/students')
def get_students():
    conn = get_db_connection()

    try:
        students = conn.execute(
            'SELECT * FROM students ORDER BY id'
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# GET STUDENT BY DATABASE ID
# ==========================================

@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()

    try:
        student = conn.execute(
            'SELECT * FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student not found"
            }), 404

        return jsonify(dict(student))

    finally:
        conn.close()


# ==========================================
# SEARCH STUDENTS BY PROGRAM
# ==========================================

@app.route('/students/program/<string:program>')
def get_students_by_program(program):
    conn = get_db_connection()

    try:
        students = conn.execute(
            '''
            SELECT * FROM students
            WHERE LOWER(program) = LOWER(?)
            ORDER BY id
            ''',
            (program,)
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# SEARCH STUDENTS BY YEAR LEVEL
# ==========================================

@app.route('/students/year/<int:year>')
def get_students_by_year(year):
    if year < 1 or year > 4:
        return jsonify({
            "error": "Year level must be between 1 and 4."
        }), 400

    conn = get_db_connection()

    try:
        students = conn.execute(
            '''
            SELECT * FROM students
            WHERE year = ?
            ORDER BY id
            ''',
            (year,)
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# SEARCH STUDENTS BY SECTION
# ==========================================

@app.route('/students/section/<string:section>')
def get_students_by_section(section):
    conn = get_db_connection()

    try:
        students = conn.execute(
            '''
            SELECT * FROM students
            WHERE LOWER(section) = LOWER(?)
            ORDER BY id
            ''',
            (section,)
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# ADD STUDENT
# POST /api/students
# RECEIVES RECORDS FROM EXTERNAL API
# ==========================================

@app.route('/api/students', methods=['POST'])
def add_student():

    raw_data = request.get_json(silent=True)

    if not isinstance(raw_data, dict):
        return jsonify({
            "error": "Please provide valid JSON data."
        }), 400

    # Default source if the sender does not provide one
    source = raw_data.get('source', 'External API')

    if not isinstance(source, str) or not source.strip():
        source = 'External API'
    else:
        source = source.strip()

    data, error = validate_student(raw_data)

    if error:
        return jsonify({
            "error": error
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            '''
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                data['student_id'],
                data['name'],
                data['program'],
                data['year'],
                data['section'],
                source
            )
        )

        conn.commit()

        return jsonify({
            "message": "Student added successfully.",
            "id": cursor.lastrowid,
            "student_id": data['student_id'],
            "name": data['name'],
            "program": data['program'],
            "year": data['year'],
            "section": data['section'],
            "source": source
        }), 201

    except sqlite3.IntegrityError:
        conn.rollback()

        return jsonify({
            "error": "Could not add student. The student ID may already exist."
        }), 409

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while adding student.")

        return jsonify({
            "error": "Database error while adding student."
        }), 500

    finally:
        conn.close()


# ==========================================
# GET STUDENT THROUGH API
# ==========================================

@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()

    try:
        student = conn.execute(
            'SELECT * FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student not found"
            }), 404

        return jsonify(dict(student)), 200

    finally:
        conn.close()


# ==========================================
# UPDATE STUDENT
# ==========================================

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)

    student, error = validate_student(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
            """,
            (
                student['student_id'],
                student['name'],
                student['program'],
                student['year'],
                student['section'],
                id
            )
        )

        if cursor.rowcount == 0:
            conn.rollback()

            return jsonify({
                "error": "Student not found"
            }), 404

        conn.commit()

        return jsonify({
            "message": "Student updated successfully.",
            "id": id
        }), 200

    except sqlite3.IntegrityError:
        conn.rollback()

        return jsonify({
            "error": "Student ID already exists."
        }), 409

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while updating student.")

        return jsonify({
            "error": "Database error while updating student."
        }), 500

    finally:
        conn.close()


# ==========================================
# DELETE STUDENT
# ==========================================

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            'DELETE FROM students WHERE id = ?',
            (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Student not found"
            }), 404

        conn.commit()

        return jsonify({
            "message": "Student deleted successfully."
        }), 200

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while deleting student.")

        return jsonify({
            "error": "Database error while deleting student."
        }), 500

    finally:
        conn.close()


# ==========================================
# GET ALL STUDENTS THROUGH API
# ==========================================

@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()

    try:
        rows = conn.execute(
            'SELECT * FROM students ORDER BY id'
        ).fetchall()

        return jsonify([dict(row) for row in rows]), 200

    finally:
        conn.close()


# ==========================================
# RETRIEVE RECORDS FROM PARTNER FLASK API
# ==========================================

# ==========================================
# RETRIEVE RECORDS FROM PARTNER AWS LIGHTSAIL
# ==========================================

@app.route('/partner-records')
def partner_records():

    partner_url = "http://3.104.184.4/api/students"

    try:
        response = requests.get(partner_url, timeout=30)
        response.raise_for_status()

        students = response.json()

        if not isinstance(students, list):
            return jsonify({
                "error": "Partner API returned an invalid student list."
            }), 502

        return jsonify(students), 200

    except requests.RequestException:
        app.logger.exception("Unable to retrieve partner AWS records.")

        return jsonify({
            "error": "Unable to connect to your classmate's AWS application."
        }), 502

    except ValueError:
        return jsonify({
            "error": "Partner API returned invalid JSON."
        }), 502

# ==========================================
# IMPORT STUDENT FROM PARTNER API
# ==========================================

@app.route('/import-student', methods=['POST'])
def import_student():

    raw_data = request.get_json(silent=True)

    student, error = validate_student(raw_data)

    if error:
        return jsonify({
            "error": error
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student['student_id'],
                student['name'],
                student['program'],
                student['year'],
                student['section'],
                'Classmate API'
            )
        )

        conn.commit()

        return jsonify({
            "message": "Remote record saved successfully.",
            "id": cursor.lastrowid,
            "student_id": student['student_id'],
            "source": "Classmate API"
        }), 201

    except sqlite3.IntegrityError:
        conn.rollback()

        return jsonify({
            "error": "This student ID already exists."
        }), 409

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while importing student.")

        return jsonify({
            "error": "Unable to import student."
        }), 500

    finally:
        conn.close()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
