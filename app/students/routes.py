from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Student, AuditLog

students_bp = Blueprint("students", __name__)


def role_required(*roles):
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name not in roles:
        return False, "Forbidden", user
    return True, None, user


@students_bp.route("/", methods=["GET"])
@jwt_required()
def list_students():
    ok, err, _ = role_required("Admin", "Teacher", "Parent")
    if not ok:
        return jsonify({"error": err}), 403
    q = Student.query
    grade = request.args.get("grade")
    if grade:
        q = q.filter_by(grade_level=grade)
    students = q.limit(200).all()
    out = []
    for s in students:
        out.append({
            "id": s.id,
            "admission_number": s.admission_number,
            "name": s.user.full_name if s.user else "",
            "email": s.user.email if s.user else "",
            "grade_level": s.grade_level,
            "gender": s.gender,
            "enrollment_date": s.enrollment_date.isoformat() if s.enrollment_date else None,
        })
    return jsonify(out)


@students_bp.route("/", methods=["POST"])
@jwt_required()
def create_student():
    ok, err, actor = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    req = ["first_name", "last_name", "email", "admission_number", "grade_level"]
    if not all(data.get(k) for k in req):
        return jsonify({"error": "Missing required fields"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409
    from app.models import Role
    role = Role.query.filter_by(name="Student").first()
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
    student = Student(
        user_id=user.id,
        admission_number=data["admission_number"],
        grade_level=data["grade_level"],
        gender=data.get("gender"),
        address=data.get("address"),
        date_of_birth=data.get("date_of_birth"),
        enrollment_date=data.get("enrollment_date"),
        parent_id=data.get("parent_id"),
        emergency_contact=data.get("emergency_contact"),
        emergency_contact_phone=data.get("emergency_contact_phone"),
        medical_info=data.get("medical_info"),
    )
    db.session.add(student)
    db.session.commit()
    AuditLog.log(actor.id, f"Created student {user.full_name}", "Student", student.id)
    return jsonify({
        "id": student.id,
        "admission_number": student.admission_number,
        "name": user.full_name,
        "email": user.email,
        "grade_level": student.grade_level,
    }), 201


@students_bp.route("/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):
    ok, err, _ = role_required("Admin", "Teacher", "Parent")
    if not ok:
        return jsonify({"error": err}), 403
    student = Student.query.get_or_404(student_id)
    return jsonify({
        "id": student.id,
        "admission_number": student.admission_number,
        "name": student.user.full_name if student.user else "",
        "email": student.user.email if student.user else "",
        "grade_level": student.grade_level,
        "gender": student.gender,
        "address": student.address,
        "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None,
        "enrollment_date": student.enrollment_date.isoformat() if student.enrollment_date else None,
        "emergency_contact": student.emergency_contact,
        "emergency_contact_phone": student.emergency_contact_phone,
    })


@students_bp.route("/<int:student_id>", methods=["PATCH"])
@jwt_required()
def update_student(student_id):
    ok, err, actor = role_required("Admin", "Teacher")
    if not ok:
        return jsonify({"error": err}), 403
    student = Student.query.get_or_404(student_id)
    data = request.get_json() or {}
    for field in ("grade_level", "gender", "address", "emergency_contact", "emergency_contact_phone", "medical_info"):
        if field in data:
            setattr(student, field, data[field])
    db.session.commit()
    AuditLog.log(actor.id, f"Updated student {student.admission_number}", "Student", student.id)
    return jsonify({"message": "Updated"})


@students_bp.route("/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    ok, err, actor = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    AuditLog.log(actor.id, f"Deleted student {student.admission_number}", "Student", student_id)
    return "", 204
