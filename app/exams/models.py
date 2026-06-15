from datetime import datetime, date
from app import db


class Exam(db.Model):
    __tablename__ = "exams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)
    grade_level = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    term = db.Column(db.String(50))
    academic_year = db.Column(db.String(20))
    instructions = db.Column(db.Text)
    passing_marks = db.Column(db.Numeric(5, 2), default=50)
    total_marks = db.Column(db.Numeric(5, 2), default=100)
    status = db.Column(db.String(30), default="Scheduled")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship("ExamResult", backref="exam", cascade="all, delete-orphan")


class ExamResult(db.Model):
    __tablename__ = "exam_results"
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"))
    marks = db.Column(db.Numeric(5, 2))
    grade = db.Column(db.String(10))
    remarks = db.Column(db.Text)
    evaluated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="exam_results")
    subject = db.relationship("Subject")
    evaluated_by = db.relationship("User")


class ReportCard(db.Model):
    __tablename__ = "report_cards"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    term = db.Column(db.String(50), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    gpa = db.Column(db.Numeric(3, 2))
    rank_in_class = db.Column(db.Integer)
    class_average = db.Column(db.Numeric(3, 2))
    teacher_comment = db.Column(db.Text)
    principal_comment = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="report_cards")


class Transcript(db.Model):
    __tablename__ = "transcripts"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    overall_gpa = db.Column(db.Numeric(3, 2))
    cumulative_rank = db.Column(db.Integer)
    total_students = db.Column(db.Integer)
    certificate_eligible = db.Column(db.Boolean, default=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="transcripts")
