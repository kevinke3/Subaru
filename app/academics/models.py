from datetime import date, datetime, time
from app import db


class Class(db.Model):
    __tablename__ = "classes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.String(50), nullable=False)
    class_teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    capacity = db.Column(db.Integer, default=40)
    room = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class_teacher = db.relationship("Teacher", backref="class_managed")
    students = db.relationship("Student", secondary="class_students", backref="classes")


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_core = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    term = db.Column(db.String(50))
    academic_year = db.Column(db.String(20))
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Active")


class TimetableEntry(db.Model):
    __tablename__ = "timetable_entries"
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"))
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    day = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50))
    term = db.Column(db.String(50))
    academic_year = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cls = db.relationship("Class", backref="timetable_entries")
    subject = db.relationship("Subject")
    teacher = db.relationship("Teacher", backref="timetable_entries")


class Assignment(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=False)
    due_date = db.Column(db.Date)
    max_score = db.Column(db.Numeric(5, 2), default=100)
    attachment_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cls = db.relationship("Class")
    subject = db.relationship("Subject")
    teacher = db.relationship("Teacher", backref="assignments")


class Grade(db.Model):
    __tablename__ = "grades"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    term = db.Column(db.String(50))
    academic_year = db.Column(db.String(20))
    score = db.Column(db.Numeric(5, 2))
    grade_letter = db.Column(db.String(5))
    remarks = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="grades")
    subject = db.relationship("Subject")
    cls = db.relationship("Class")
    created_by = db.relationship("User")


class ClassStudents(db.Model):
    __tablename__ = "class_students"
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"))
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
