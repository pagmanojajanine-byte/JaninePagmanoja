from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import requests

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# Home page
@app.route('/')
def home():
    return render_template('index.html')


# Student Information API
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00186",
        "name": "Janine Pagmanoja",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# Greeting API
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student').strip()

    if not name:
        name = 'Student'

    return jsonify({"message": f"Hello, {name}!"})


# Course Information API
@app.route('/course')
def get_course():
    return jsonify({
        "course_code": "IT3120",
        "course_name": "System Integration",
        "units": 3,
        "semester": "First Semester"
    })


# Grade Checker API
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


# Get all students
@app.route('/students')
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students ORDER BY id'
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# Get a student by database ID
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# 18. Search students by program
@app.route('/students/program/<string:program>')
def get_students_by_program(program):
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students WHERE LOWER(program) = LOWER(?) ORDER BY id',
        (program,)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# 19. Search students by year level
@app.route('/students/year/<int:year>')
def get_students_by_year(year):
    if year < 1 or year > 4:
        return jsonify({
            "error": "Year level must be between 1 and 4."
        }), 400

    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students WHERE year = ? ORDER BY id',
        (year,)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# 20. Search students by section
@app.route('/students/section/<string:section>')
def get_students_by_section(section):
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students WHERE LOWER(section) = LOWER(?) ORDER BY id',
        (section,)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route('/api/students', methods=['POST'])
def add_student():
    raw_data = request.get_json(silent=True) or {}
    source = raw_data.get('source', 'External API')

    data, error = validate_student(raw_data)
    if error:
        return jsonify({'error': error}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['student_id'],
            data['name'],
            data['program'],
            data['year'],
            data['section'],
            source
        ))

        conn.commit()

        return jsonify({
            'message': 'Student added successfully.',
            'id': cursor.lastrowid,
            'source': source
        }), 201

    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({
            'error': 'Could not add student. The student ID may already exist.'
        }), 409

    finally:
        conn.close()

# GET: Retrieve a student by ID
@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student)), 200


# PUT: Update a student
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()

    conn = get_db_connection()

    cursor = conn.execute(
        """
        UPDATE students
        SET student_id = ?, name = ?, program = ?,
            year = ?, section = ?
        WHERE id = ?
        """,
        (
            data['student_id'],
            data['name'],
            data['program'],
            data['year'],
            data['section'],
            id
        )
    )

    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student updated"}), 200


# DELETE: Delete a student
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    cursor = conn.execute(
        'DELETE FROM students WHERE id = ?',
        (id,)
    )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted"}), 200


@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()

    rows = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows]), 200


# Retrieve records from Partner Flask API
@app.route('/partner-records')
def partner_records():
    partner_url = "https://jarellkrismagarso-1.onrender.com/api/students"

    try:
        response = requests.get(partner_url, timeout=15)
        response.raise_for_status()

        return jsonify(response.json())

    except requests.RequestException:
        return jsonify({
            "error": "Unable to retrieve partner data"
        }), 502


# Import a student from Partner API
@app.route('/import-student', methods=['POST'])
def import_student():
    data = request.get_json()
    conn = get_db_connection()

    try:
        conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data['student_id'],
                data['name'],
                data['program'],
                data['year'],
                data['section'],
                'Classmate API'
            )
        )

        conn.commit()

        return jsonify({
            "message": "Remote record saved"
        }), 201

    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True, port=5001)