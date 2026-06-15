from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.analytics.models import DashboardMetric, ActivityLog, SchoolStats

analytics_bp = Blueprint("analytics", __name__)


def role_required(*roles):
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name not in roles:
        return False, "Forbidden", user
    return True, None, user


@analytics_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard_metrics():
    ok, err, _ = role_required("Admin", "Teacher", "Student", "Parent")
    if not ok:
        return jsonify({"error": err}), 403
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    metrics = DashboardMetric.query.all()
    out = {
        "total_students": SchoolStats.get("total_students"),
        "total_teachers": SchoolStats.get("total_teachers"),
        "total_classes": SchoolStats.get("total_classes"),
        "revenue_collected": SchoolStats.get("revenue_collected"),
        "pending_invoices": SchoolStats.get("pending_invoices"),
        "attendance_today": SchoolStats.get("attendance_today"),
        "upcoming_events": SchoolStats.get("upcoming_events", 0),
        "active_notifications": SchoolStats.get("active_notifications", 0),
    }
    return jsonify(out)


@analytics_bp.route("/recent-activity", methods=["GET"])
@jwt_required()
def recent_activity():
    ok, err, _ = role_required("Admin", "Teacher")
    if not ok:
        return jsonify({"error": err}), 403
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(20).all()
    return jsonify([{
        "id": l.id,
        "action": l.action,
        "actor": l.actor.full_name if l.actor else "System",
        "target_type": l.target_type,
        "target_id": l.target_id,
        "created_at": l.created_at.isoformat(),
    } for l in logs])
