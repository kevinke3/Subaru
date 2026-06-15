from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    return jsonify(user.to_dict())


@settings_bp.route("/profile", methods=["PATCH"])
@jwt_required()
def update_profile():
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    data = request.get_json() or {}
    for field in ("first_name", "last_name", "phone_number", "avatar_url"):
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return jsonify(user.to_dict())


@settings_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    data = request.get_json() or {}
    current = data.get("current_password", "")
    new = data.get("new_password", "")
    if not user.check_password(current):
        return jsonify({"error": "Invalid current password"}), 400
    user.set_password(new)
    db.session.commit()
    return jsonify({"message": "Password changed"})


@settings_bp.route("/notification-preferences", methods=["GET"])
@jwt_required()
def get_notification_prefs():
    return jsonify({
        "email": True,
        "sms": False,
        "push": True,
        "fee_reminders": True,
        "attendance_alerts": True,
        "assignment_deadlines": True,
        "exam_schedules": True,
        "announcements": True,
    })


@settings_bp.route("/notification-preferences", methods=["PATCH"])
@jwt_required()
def update_notification_prefs():
    data = request.get_json() or {}
    # saved per user in a separate table in production
    return jsonify(data)
