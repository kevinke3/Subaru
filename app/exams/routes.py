from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.exams.models import Exam, ExamResult, ReportCard, Transcript
from app.models import User, Student, AuditLog

exams_bp = Blueprint("exams", __name__)


def role_required(*roles):
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name not in roles:
        return False, "Forbidden", user
    return True, None, user


@exams_bp.route("/exams", methods=["GET"])
@jwt_required()
def list_exams():
    ok, err, _ = role_required("Admin", "Teacher", "Student", "Parent")
    if not ok:
        return jsonify({"error": err}), 403
    q = Exam.query
    grade = request.args.get("grade")
    if grade:
        q = q.filter_by(grade_level=grade)
    exams = q.order_by(Exam.start_date.desc()).limit(50).all()
    return jsonify([{
        "id": e.id,
        "name": e.name,
        "exam_type": e.exam_type,
        "grade_level": e.grade_level,
        "start_date": e.start_date.isoformat() if e.start_date else None,
        "end_date": e.end_date.isoformat() if e.end_date else None,
        "status": e.status,
        "term": e.term,
        "academic_year": e.academic_year,
    } for e in exams])


@exams_bp.route("/exams", methods=["POST"])
@jwt_required()
def create_exam():
    ok, err, actor = role_required("Admin", "Teacher")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    exam = Exam(
        name=data.get("name"),
        exam_type=data.get("exam_type"),
        grade_level=data.get("grade_level"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        term=data.get("term"),
        academic_year=data.get("academic_year"),
        instructions=data.get("instructions"),
        passing_marks=data.get("passing_marks", 50),
        total_marks=data.get("total_marks", 100),
    )
    db.session.add(exam)
    db.session.commit()
    AuditLog.log(actor.id, f"Created exam {exam.name}", "Exam", exam.id)
    return jsonify({"id": exam.id, "name": exam.name}), 201


@exams_bp.route("/results", methods=["POST"])
@jwt_required()
def add_result():
    ok, err, actor = role_required("Admin", "Teacher")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    result = ExamResult(
        exam_id=data.get("exam_id"),
        student_id=data.get("student_id"),
        subject_id=data.get("subject_id"),
        marks=data.get("marks"),
        grade=data.get("grade"),
        remarks=data.get("remarks"),
        evaluated_by_id=actor.id,
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({"id": result.id}), 201


@exams_bp.route("/results", methods=["GET"])
@jwt_required()
def list_results():
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    q = ExamResult.query.join(Exam)
    if user.role.name == "Student":
        student = Student.query.filter_by(user_id=user.id).first_or_404()
        q = q.filter(ExamResult.student_id == student.id)
    elif user.role.name == "Parent":
        child = Student.query.filter_by(parent_id=user.id).first_or_404()
        q = q.filter(ExamResult.student_id == child.id)
    exam_id = request.args.get("exam_id", type=int)
    if exam_id:
        q = q.filter(ExamResult.exam_id == exam_id)
    results = q.limit(200).all()
    out = []
    for r in results:
        out.append({
            "id": r.id,
            "exam_name": r.exam.name if r.exam else "",
            "student_name": r.student.user.full_name if r.student and r.student.user else "",
            "subject_name": r.subject.name if r.subject else "",
            "marks": r.marks,
            "grade": r.grade,
            "remarks": r.remarks,
        })
    return jsonify(out)


@exams_bp.route("/report-cards/<int:student_id>", methods=["GET"])
@jwt_required()
def get_report_card(student_id):
    ok, err, _ = role_required("Admin", "Teacher", "Student", "Parent")
    if not ok:
        return jsonify({"error": err}), 403
    term = request.args.get("term")
    ay = request.args.get("academic_year")
    q = ReportCard.query.filter_by(student_id=student_id)
    if term:
        q = q.filter_by(term=term)
    if ay:
        q = q.filter_by(academic_year=ay)
    rc = q.order_by(ReportCard.created_at.desc()).first()
    if not rc:
        return jsonify({"error": "Report card not found"}), 404
    return jsonify({
        "id": rc.id,
        "student_name": rc.student.user.full_name if rc.student and rc.student.user else "",
        "term": rc.term,
        "academic_year": rc.academic_year,
        "gpa": rc.gpa,
        "rank_in_class": rc.rank_in_class,
        "class_average": rc.class_average,
        "teacher_comment": rc.teacher_comment,
        "principal_comment": rc.principal_comment,
        "generated_at": rc.generated_at.isoformat() if rc.generated_at else None,
    })


@exams_bp.route("/transcripts/<int:student_id>", methods=["GET"])
@jwt_required()
def get_transcript(student_id):
    ok, err, _ = role_required("Admin", "Teacher", "Student", "Parent")
    if not ok:
        return jsonify({"error": err}), 403
    ay = request.args.get("academic_year")
    q = Transcript.query.filter_by(student_id=student_id)
    if ay:
        q = q.filter_by(academic_year=ay)
    t = q.first()
    if not t:
        return jsonify({"error": "Transcript not found"}), 404
    return jsonify({
        "id": t.id,
        "student_name": t.student.user.full_name if t.student and t.student.user else "",
        "academic_year": t.academic_year,
        "overall_gpa": t.overall_gpa,
        "cumulative_rank": t.cumulative_rank,
        "total_students": t.total_students,
        "certificate_eligible": t.certificate_eligible,
    })
