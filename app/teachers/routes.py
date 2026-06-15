from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Teacher, AuditLog

teachers_bp = Blueprint("teachers", __name__)


def role_required(*roles):
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name not in roles:
        return False, "Forbidden", user
    return True, None, user


@teachers_bp.route("/", methods=["GET"])
@jwt_required()
def list_teachers():
    ok, err, _ = role_required("Admin", "Teacher")
    if not ok:
        return jsonify({"error": err}), 403
    dept = request.args.get("department")
    q = Teacher.query
    if dept:
        q = q.filter_by(department=dept)
    teachers = q.limit(200).all()
    out = []
    for t in teachers:
        out.append({
            "id": t.id,
            "employee_number": t.employee_number,
            "name": t.user.full_name if t.user else "",
            "email": t.user.email if t.user else "",
            "department": t.department,
            "qualification": t.qualification,
            "specialization": t.specialization,
            "hire_date": t.hire_date.isoformat() if t.hire_date else None,
        })
    return jsonify(out)


@teachers_bp.route("/", methods=["POST"])
@jwt_required()
def create_teacher():
    ok, err, actor = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    req = ["first_name", "last_name", "email", "employee_number", "department"]
    if not all(data.get(k) for k in req):
        return jsonify({"error": "Missing required fields"}), 400
    existing = User.query.filter_by(email=data["email"]).first()
    if existing:
        return jsonify({"error": "Email already exists"}), 409
    from app.models import Role
    role = Role.query.filter_by(name="Teacher").first()
    user = User(
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone_number=data.get("phone_number"),
        role_id=role.id,
    )
    user.set_password(data.get("password", "changeme123"))
    db.session.add(user)
    db.session.flush()
    teacher = Teacher(
        user_id=user.id,
        employee_number=data["employee_number"],
        department=data["department"],
        qualification=data.get("qualification"),
        specialization=data.get("specialization"),
        hire_date=data.get("hire_date"),
    )
    db.session.add(teacher)
    db.session.commit()
    AuditLog.log(actor.id, f"Created teacher {user.full_name}", "Teacher", teacher.id)
    return jsonify({
        "id": teacher.id,
        "employee_number": teacher.employee_number,
        "name": user.full_name,
        "email": user.email,
        "department": teacher.department,
    }), 201


@teachers_bp.route("/<int:teacher_id>", methods=["GET"])
@jwt_required()
def get_teacher(teacher_id):
    ok, err, _ = role_required("Admin", "Teacher")
    if not ok:
        return jsonify({"error": err}), 403
    teacher = Teacher.query.get_or_404(teacher_id)
    return jsonify({
        "id": teacher.id,
        "employee_number": teacher.employee_number,
        "name": teacher.user.full_name if teacher.user else "",
        "email": teacher.user.email if teacher.user else "",
        "department": teacher.department,
        "qualification": teacher.qualification,
        "specialization": teacher.specialization,
        "hire_date": teacher.hire_date.isoformat() if teacher.hire_date else None,
    })


@teachers_bp.route("/<int:teacher_id>", methods=["PATCH"])
@jwt_required()
def update_teacher(teacher_id):
    ok, err, actor = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    teacher = Teacher.query.get_or_404(teacher_id)
    data = request.get_json() or {}
    for field in ("department", "qualification", "specialization"):
        if field in data:
            setattr(teacher, field, data[field])
    db.session.commit()
    AuditLog.log(actor.id, f"Updated teacher {teacher.employee_number}", "Teacher", teacher.id)
    return jsonify({"message": "Updated"})
