from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.attendance.models import AttendanceSession, AttendanceRecord, AttendanceSummary, LeaveRequest
from app.models import User, Student

attendance_bp = Blueprint("attendance", __name__)


def role_required(*roles):
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name not in roles:
        return False, "Forbidden", user
    return True, None, user


@attendance_bp.route("/sessions", methods=["GET"])
@jwt_required()
def list_sessions():
    ok, err, _ = role_required("Admin", "Teacher")
    if not ok:
        return jsonify({"error": err}), 403
    sessions = AttendanceSession.query.limit(50).all()
    return jsonify([{
        "id": s.id,
        "date": s.date.isoformat(),
        "class_name": s.class_obj.name if s.class_obj else "",
        "subject": s.subject.name if s.subject else "",
        "teacher": s.teacher.user.full_name if s.teacher and s.teacher.user else "",
        "status": s.status,
    } for s in sessions])


@attendance_bp.route("/sessions", methods=["POST"])
@jwt_required()
def create_session():
    ok, err, actor = role_required("Teacher", "Admin")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    session = AttendanceSession(
        class_id=data.get("class_id"),
        subject_id=data.get("subject_id"),
        teacher_id=data.get("teacher_id", actor.teacher_profile.id if actor.role.name == "Teacher" else None),
        date=data.get("date"),
        note=data.get("note"),
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({"id": session.id}), 201


@attendance_bp.route("/records", methods=["POST"])
@jwt_required()
def mark_attendance():
    ok, err, actor = role_required("Teacher", "Admin")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    session_id = data.get("session_id")
    student_id = data.get("student_id")
    status = data.get("status")
    if not all([session_id, student_id, status]):
        return jsonify({"error": "Missing fields"}), 400
    record = AttendanceRecord(
        session_id=session_id,
        student_id=student_id,
        status=status,
        remarks=data.get("remarks"),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({"id": record.id}), 201


@attendance_bp.route("/summary", methods=["GET"])
@jwt_required()
def attendance_summary():
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name == "Student":
        student = Student.query.filter_by(user_id=user.id).first_or_404()
        summaries = AttendanceSummary.query.filter_by(student_id=student.id).all()
    elif user.role.name == "Parent":
        child = Student.query.filter_by(parent_id=user.id).first()
        if not child:
            return jsonify({"error": "No linked student"}), 404
        summaries = AttendanceSummary.query.filter_by(student_id=child.id).all()
    else:
        class_id = request.args.get("class_id", type=int)
        student_id = request.args.get("student_id", type=int)
        q = AttendanceSummary.query
        if class_id:
            q = q.filter_by(class_id=class_id)
        if student_id:
            q = q.filter_by(student_id=student_id)
        summaries = q.limit(50).all()
    out = []
    for s in summaries:
        out.append({
            "student_id": s.student_id,
            "student_name": s.student.user.full_name if s.student and s.student.user else "",
            "term": s.term,
            "present": s.present,
            "absent": s.absent,
            "late": s.late,
            "percentage": round((s.present / max(s.present + s.absent + s.late, 1)) * 100, 1),
        })
    return jsonify(out)


@attendance_bp.route("/leave-requests", methods=["POST"])
@jwt_required()
def create_leave_request():
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name not in ("Admin", "Parent"):
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json() or {}
    lr = LeaveRequest(
        student_id=data.get("student_id"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        reason=data.get("reason"),
        requested_by_id=user.id,
    )
    db.session.add(lr)
    db.session.commit()
    return jsonify({"id": lr.id, "status": lr.status}), 201


@attendance_bp.route("/leave-requests", methods=["GET"])
@jwt_required()
def list_leave_requests():
    ok, err, _ = role_required("Admin", "Teacher", "Parent")
    if not ok:
        return jsonify({"error": err}), 403
    q = LeaveRequest.query
    student_id = request.args.get("student_id", type=int)
    if student_id:
        q = q.filter_by(student_id=student_id)
    items = q.order_by(LeaveRequest.created_at.desc()).limit(50).all()
    out = []
    for lr in items:
        out.append({
            "id": lr.id,
            "student_name": lr.student.user.full_name if lr.student and lr.student.user else "",
            "start_date": lr.start_date,
            "end_date": lr.end_date,
            "reason": lr.reason,
            "status": lr.status,
            "created_at": lr.created_at.isoformat(),
        })
    return jsonify(out)
