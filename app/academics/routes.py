from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, AuditLog
from app.academics.models import Class, Subject, Enrollment, TimetableEntry

academics_bp = Blueprint("academics", __name__)


def role_required(*roles):
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name not in roles:
        return False, "Forbidden", user
    return True, None, user


@academics_bp.route("/classes", methods=["GET"])
@jwt_required()
def list_classes():
    ok, err, _ = role_required("Admin", "Teacher", "Student")
    if not ok:
        return jsonify({"error": err}), 403
    classes = Class.query.limit(200).all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "grade_level": c.grade_level,
        "class_teacher": c.class_teacher.user.full_name if c.class_teacher and c.class_teacher.user else "",
        "capacity": c.capacity,
        "student_count": len(c.students),
    } for c in classes])


@academics_bp.route("/classes", methods=["POST"])
@jwt_required()
def create_class():
    ok, err, actor = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    name = data.get("name")
    grade_level = data.get("grade_level")
    if not name or not grade_level:
        return jsonify({"error": "Missing required fields"}), 400
    cls = Class(
        name=name,
        grade_level=grade_level,
        capacity=data.get("capacity", 40),
        class_teacher_id=data.get("class_teacher_id"),
    )
    db.session.add(cls)
    db.session.commit()
    AuditLog.log(actor.id, f"Created class {name}", "Class", cls.id)
    return jsonify({"id": cls.id, "name": cls.name}), 201


@academics_bp.route("/subjects", methods=["GET"])
@jwt_required()
def list_subjects():
    ok, err, _ = role_required("Admin", "Teacher", "Student")
    if not ok:
        return jsonify({"error": err}), 403
    subjects = Subject.query.limit(200).all()
    return jsonify([{"id": s.id, "name": s.name, "code": s.code, "description": s.description} for s in subjects])


@academics_bp.route("/timetable", methods=["GET"])
@jwt_required()
def get_timetable():
    ok, err, _ = role_required("Admin", "Teacher", "Student")
    if not ok:
        return jsonify({"error": err}), 403
    class_id = request.args.get("class_id", type=int)
    q = TimetableEntry.query
    if class_id:
        q = q.filter_by(class_id=class_id)
    entries = q.limit(200).all()
    out = []
    for e in entries:
        out.append({
            "id": e.id,
            "day": e.day,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "subject": e.subject.name if e.subject else "",
            "teacher": e.teacher.user.full_name if e.teacher and e.teacher.user else "",
            "class_name": e.cls.name if e.cls else "",
        })
    return jsonify(out)
