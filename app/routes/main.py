from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/login")
def login_page():
    return render_template("login.html")

@main_bp.route("/register")
def register_page():
    return render_template("register.html")

@main_bp.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@main_bp.route("/students")
def students_page():
    return render_template("students.html")

@main_bp.route("/teachers")
def teachers_page():
    return render_template("teachers.html")

@main_bp.route("/academics")
def academics_page():
    return render_template("academics.html")

@main_bp.route("/attendance")
def attendance_page():
    return render_template("attendance.html")

@main_bp.route("/finance")
def finance_page():
    return render_template("finance.html")

@main_bp.route("/exams")
def exams_page():
    return render_template("exams.html")

@main_bp.route("/messages")
def messages_page():
    return render_template("messages.html")

@main_bp.route("/settings")
def settings_page():
    return render_template("settings.html")

@main_bp.route("/student-portal")
def student_portal_page():
    return render_template("student-portal.html")

@main_bp.route("/teacher-portal")
def teacher_portal_page():
    return render_template("teacher-portal.html")

@main_bp.route("/parent-portal")
def parent_portal_page():
    return render_template("parent-portal.html")

@main_bp.route("/administration")
def administration_page():
    return render_template("administration.html")
