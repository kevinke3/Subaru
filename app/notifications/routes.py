from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.notifications.models import Notification

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = int(get_jwt_identity())  # simplified: assumes Notification.user_id set
    q = Notification.query.filter_by(user_id=user_id)
    q = q.order_by(Notification.created_at.desc()).limit(50)
    items = q.all()
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "body": n.body,
        "type": n.type,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
    } for n in items])
