
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


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
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.execute(
        """
        INSERT INTO students
        (student_id, name, program, year, section)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data['student_id'],
            data['name'],
            data['program'],
            data['year'],
            data['section']
        )
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Student added",
        "id": new_id
    }), 201
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
if __name__ == '__main__':
    app.run(debug=True, port=5001)
