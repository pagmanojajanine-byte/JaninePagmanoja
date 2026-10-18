from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/student')
def get_student():
    return jsonify({
"student_id": "24-00186",
"name": "Janine Pagmanoja",
"program": "BSIT",
"year": 3,
"section": "B"
})
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
"message": f"Hello, {name}!"
})

@app.route('/course')
def get_course():
    return jsonify({
        "course_code": "IT3120",
        "course_name": "System Integration",
        "units": 3,
        "semester": "First Semester"
    })

@app.route('/grade')
def get_grade():
    score = request.args.get('score', type=float)

    if score is None:
        return jsonify({
            "error": "Please provide a score."
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)
