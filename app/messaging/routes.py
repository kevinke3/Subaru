from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.messaging.models import Conversation, Message, Announcement
from app.models import User, AuditLog

messaging_bp = Blueprint("messaging", __name__)


def role_required(*roles):
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name not in roles:
        return False, "Forbidden", user
    return True, None, user


@messaging_bp.route("/conversations", methods=["GET"])
@jwt_required()
def list_conversations():
    uid = int(get_jwt_identity())
    convs = Conversation.query.filter(
        (Conversation.participant_one_id == uid) | (Conversation.participant_two_id == uid)
    ).all()
    out = []
    for c in convs:
        other_id = c.participant_two_id if c.participant_one_id == uid else c.participant_one_id
        other = User.query.get(other_id)
        out.append({
            "id": c.id,
            "participant": other.full_name if other else "",
            "role": other.role.name if other else "",
            "last_message": c.last_message or "",
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            "unread_count": c.unread_count(uid),
        })
    return jsonify(out)


@messaging_bp.route("/conversations/<int:conv_id>/messages", methods=["GET"])
@jwt_required()
def list_messages(conv_id):
    uid = int(get_jwt_identity())
    conversation = Conversation.query.get_or_404(conv_id)
    if uid not in (conversation.participant_one_id, conversation.participant_two_id):
        return jsonify({"error": "Forbidden"}), 403
    messages = Message.query.filter_by(conversation_id=conv_id).order_by(Message.created_at.asc()).all()
    return jsonify([{
        "id": m.id,
        "sender": m.sender.full_name if m.sender else "",
        "body": m.body,
        "created_at": m.created_at.isoformat(),
        "is_read": m.is_read,
    } for m in messages])


@messaging_bp.route("/conversations/<int:conv_id>/messages", methods=["POST"])
@jwt_required()
def send_message(conv_id):
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    body = data.get("body")
    if not body:
        return jsonify({"error": "Message body required"}), 400
    conversation = Conversation.query.get_or_404(conv_id)
    if uid not in (conversation.participant_one_id, conversation.participant_two_id):
        return jsonify({"error": "Forbidden"}), 403
    msg = Message(
        conversation_id=conv_id,
        sender_id=uid,
        body=body,
    )
    conversation.last_message = body
    conversation.updated_at = db.func.now()
    db.session.add(msg)
    db.session.commit()
    return jsonify({"id": msg.id, "body": msg.body}), 201


@messaging_bp.route("/conversations", methods=["POST"])
@jwt_required()
def start_conversation():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    participant_id = data.get("participant_id")
    if not participant_id:
        return jsonify({"error": "participant_id required"}), 400
    existing = Conversation.query.filter(
        ((Conversation.participant_one_id == uid) & (Conversation.participant_two_id == participant_id)) |
        ((Conversation.participant_one_id == participant_id) & (Conversation.participant_two_id == uid))
    ).first()
    if existing:
        return jsonify({"id": existing.id})
    conv = Conversation(participant_one_id=uid, participant_two_id=participant_id)
    db.session.add(conv)
    db.session.commit()
    return jsonify({"id": conv.id}), 201


@messaging_bp.route("/announcements", methods=["GET"])
@jwt_required()
def list_announcements():
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    q = Announcement.query
    if user.role.name == "Student":
        q = q.filter((Announcement.target_roles.contains(["Student"])) | (Announcement.target_roles == []))
    elif user.role.name == "Parent":
        q = q.filter((Announcement.target_roles.contains(["Parent"])) | (Announcement.target_roles == []))
    elif user.role.name == "Teacher":
        q = q.filter((Announcement.target_roles.contains(["Teacher"])) | (Announcement.target_roles == []))
    items = q.order_by(Announcement.created_at.desc()).limit(50).all()
    return jsonify([{
        "id": a.id,
        "title": a.title,
        "body": a.body,
        "priority": a.priority,
        "created_at": a.created_at.isoformat(),
    } for a in items])


@messaging_bp.route("/announcements", methods=["POST"])
@jwt_required()
def create_announcement():
    ok, err, actor = role_required("Admin", "Teacher")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    a = Announcement(
        title=data.get("title"),
        body=data.get("body"),
        priority=data.get("priority", "Normal"),
        target_roles=data.get("target_roles", []),
        created_by_id=actor.id,
    )
    db.session.add(a)
    db.session.commit()
    AuditLog.log(actor.id, f"Posted announcement {a.title}", "Announcement", a.id)
    return jsonify({"id": a.id, "title": a.title}), 201
