from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, AuditLog

admin_bp = Blueprint("admin", __name__)


def admin_required():
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if not user.has_permission("manage_users"):
        return False, "Forbidden"
    return True, user


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    ok, result = admin_required()
    if ok is False:
        return jsonify({"error": result}), 403
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@admin_bp.route("/users/<int:user_id>", methods=["PATCH"])
@jwt_required()
def update_user(user_id):
    ok, result = admin_required()
    if ok is False:
        return jsonify({"error": result}), 403
    actor = result
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    for field in ("first_name", "last_name", "phone_number", "is_active"):
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    AuditLog.log(actor.id, f"Updated user {user.email}", "User", user.id)
    return jsonify(user.to_dict())


@admin_bp.route("/audit-logs", methods=["GET"])
@jwt_required()
def audit_logs():
    ok, result = admin_required()
    if ok is False:
        return jsonify({"error": result}), 403
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return jsonify([l.to_dict() for l in logs])
