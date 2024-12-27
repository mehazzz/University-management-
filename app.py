from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key"

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('university_management.db')
    conn.row_factory = sqlite3.Row
    return conn

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['user_id'], user['username'], user['password'])
    return None

# Initialize the database with all necessary tables and triggers
def initialize_db():
    conn = get_db_connection()
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS Departments (
        department_id INTEGER PRIMARY KEY,
        department_name TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS Faculties (
        faculty_id INTEGER PRIMARY KEY,
        faculty_name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS Studentsssss (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department_name TEXT,
        year INTEGER CHECK(year BETWEEN 1 AND 4),
        email TEXT UNIQUE,
        phone TEXT,
        enrollment_date DATE DEFAULT (DATE('now')),
        FOREIGN KEY (department_name) REFERENCES Departments(department_name)
    );
    CREATE TABLE IF NOT EXISTS Courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        department_name TEXT,
        credits INTEGER CHECK(credits > 0),
        course_code TEXT UNIQUE,
        FOREIGN KEY (department_name) REFERENCES Departments(department_name)
    );
    
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Enrollmentss (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        action TEXT,
        action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TRIGGER IF NOT EXISTS log_student_insert
    AFTER INSERT ON Studentsssss
    BEGIN
        INSERT INTO Enrollmentss (student_id, action)
        VALUES (NEW.student_id, 'INSERT');
    END;

    CREATE TRIGGER IF NOT EXISTS log_student_delete
    AFTER DELETE ON Studentsssss
    BEGIN
        INSERT INTO Enrollmentss (student_id, action)
        VALUES (OLD.student_id, 'DELETE');
    END;

    CREATE TRIGGER IF NOT EXISTS log_student_update
    AFTER UPDATE ON Studentsssss
    BEGIN
        INSERT INTO Enrollmentss (student_id, action)
        VALUES (NEW.student_id, 'UPDATE');
    END;

    CREATE TRIGGER IF NOT EXISTS check_course_credits
    BEFORE INSERT ON Courses
    BEGIN
        SELECT CASE
            WHEN NEW.credits < 1 THEN
                RAISE (ABORT, 'Credits must be greater than zero')
        END;
    END;
    ''')
    conn.commit()
    conn.close()

initialize_db()

# Routes
@app.route('/')
def home_redirect():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and user['password'] == password:
            login_user(User(user['user_id'], user['username'], user['password']))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO Users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken', 'danger')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    if request.method == 'POST':
        department_name = request.form['department_name']

        if not department_name:
            flash("Department name is required!", "danger")
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO Departments (department_name) VALUES (?)', (department_name,))
            conn.commit()
            conn.close()
            flash("Department added successfully!", "success")
            return redirect(url_for('dashboard'))

    return render_template('add_department.html')

@app.route('/add_faculty', methods=['GET', 'POST'])
@login_required
def add_faculty():
    if request.method == 'POST':
        faculty_name = request.form.get('faculty_name')

        if not faculty_name:
            flash("Faculty name is required!", "danger")
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO Faculties (faculty_name) VALUES (?)', (faculty_name,))
            conn.commit()
            conn.close()
            flash("Faculty added successfully!", "success")
            return redirect(url_for('dashboard'))

    return render_template('add_faculty.html')

@app.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    conn = get_db_connection()
    departments = conn.execute('SELECT department_name FROM Departments').fetchall()
    conn.close()

    if request.method == 'POST':
        course_name = request.form.get('course_name')
        department_name = request.form.get('department_name')
        credits = request.form.get('credits')
        course_code = request.form.get('course_code')

        if not course_name or not department_name or not credits or not course_code:
            flash("All fields are required!", "danger")
        else:
            try:
                conn = get_db_connection()
                conn.execute('INSERT INTO Courses (course_name, department_name, credits, course_code) VALUES (?, ?, ?, ?)',
                             (course_name, department_name, credits, course_code))
                conn.commit()
                conn.close()
                flash("Course added successfully!", "success")
            except sqlite3.IntegrityError:
                flash("A course with this code already exists.", "danger")

            return redirect(url_for('dashboard'))

    return render_template('add_course.html', departments=departments)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    conn = get_db_connection()
    departments = conn.execute('SELECT department_name FROM Departments').fetchall()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        department_name = request.form['department_name']
        year = request.form['year']
        email = request.form['email']
        phone = request.form['phone']

        if not name or not department_name or not year:
            flash("All fields are required!", "danger")
        else:
            try:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO Studentsssss (name, department_name, year, email, phone)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, department_name, year, email, phone))
                conn.commit()
                flash("Student added successfully!", "success")
            except sqlite3.IntegrityError:
                flash("A student with this email already exists.", "danger")
            finally:
                conn.close()
            return redirect(url_for('dashboard'))

    return render_template('add_student.html', departments=departments)

@app.route('/view_students')
@login_required
def view_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM Studentsssss').fetchall()
    conn.close()
    return render_template('view_students.html', students=students)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Studentsssss WHERE student_id = ?', (student_id,))
    conn.commit()
    conn.close()
    flash("Student deleted successfully!", "success")
    return redirect(url_for('view_students'))

@app.route('/update_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def update_student(student_id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM Studentsssss WHERE student_id = ?', (student_id,)).fetchone()
    departments = conn.execute('SELECT department_name FROM Departments').fetchall()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        department_name = request.form['department_name']
        year = request.form['year']
        email = request.form['email']
        phone = request.form['phone']

        conn = get_db_connection()
        conn.execute('''
            UPDATE Studentsssss
            SET name = ?, department_name = ?, year = ?, email = ?, phone = ?
            WHERE student_id = ?
        ''', (name, department_name, year, email, phone, student_id))
        conn.commit()
        conn.close()
        flash("Student updated successfully!", "success")
        return redirect(url_for('view_students'))

    return render_template('update_student.html', student=student, departments=departments)

@app.route('/view_departments')
@login_required
def view_departments():
    conn = get_db_connection()
    departments = conn.execute('SELECT * FROM Departments').fetchall()
    conn.close()
    return render_template('view_departments.html', departments=departments)

@app.route('/view_students_by_department')
@login_required
def view_students_by_department():
    conn = get_db_connection()
    students = conn.execute('''
        SELECT d.department_name, s.name, s.phone
        FROM Studentsssss s
        JOIN Departments d ON s.department_name = d.department_name
        GROUP BY d.department_name, s.name
    ''').fetchall()
    conn.close()
    return render_template('view_students_by_department.html', students=students)

if __name__ == "__main__":
    app.run(debug=True)
