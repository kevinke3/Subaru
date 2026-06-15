from datetime import datetime, date, time
from app import db


class AttendanceSession(db.Model):
    __tablename__ = "attendance_sessions"
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"))
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    date = db.Column(db.Date, default=date.today)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    status = db.Column(db.String(30), default="Open")
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class_obj = db.relationship("Class")
    subject = db.relationship("Subject")
    teacher = db.relationship("Teacher", backref="attendance_sessions")
    records = db.relationship("AttendanceRecord", back_populates="attendance_session", cascade="all, delete-orphan")


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    remarks = db.Column(db.Text)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendance_session = db.relationship("AttendanceSession", back_populates="records")
    student = db.relationship("Student", backref="attendance_records")
    recorded_by = db.relationship("User")


class AttendanceSummary(db.Model):
    __tablename__ = "attendance_summaries"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"))
    term = db.Column(db.String(50))
    academic_year = db.Column(db.String(20))
    present = db.Column(db.Integer, default=0)
    absent = db.Column(db.Integer, default=0)
    late = db.Column(db.Integer, default=0)
    total_days = db.Column(db.Integer, default=0)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="attendance_summaries")
    cls = db.relationship("Class")


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    requested_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    review_note = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="leave_requests")
    requested_by = db.relationship("User", foreign_keys=[requested_by_id])
    reviewed_by = db.relationship("User", foreign_keys=[reviewed_by_id])
