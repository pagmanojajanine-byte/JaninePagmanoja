
import sqlite3

# Connect to the database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create the students table if it does not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
''')

# Remove old sample records
cursor.execute('DELETE FROM students')

# Insert at least five student records
students = [
    ('2026-00123', 'Jero Paca-oncis', 'BSIT', 1, 'A'),
    ('2026-00124', 'Hapee Malunes', 'BSIT', 1, 'B'),
    ('2026-00125', 'Jarell Kris Magarso', 'BSIT', 2, 'A'),
    ('2026-00126', 'Janine Pagmanoja', 'BSIT', 2, 'B'),
    ('2026-00127', 'Clarisse Paclibar', 'BSIT', 3, 'A'),
    ('2026-00128', 'Jezalyn Indic', 'BSIT', 3, 'B')
]

cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
''', students)

# Save changes
conn.commit()
conn.close()

print("Database initialized successfully!")
print("Six student records have been added.")
