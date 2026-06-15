from datetime import datetime
from app import db


class Conversation(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    participant_one_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    participant_two_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship("Message", backref="conversation", cascade="all, delete-orphan")

    def unread_count(self, user_id):
        return Message.query.filter(
            Message.conversation_id == self.id,
            Message.sender_id != user_id,
            Message.is_read.is_(False),
        ).count()


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("User", backref="messages_sent")


class Announcement(db.Model):
    __tablename__ = "announcements"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default="Normal")
    target_roles = db.Column(db.Text)  # JSON array of role names
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_by = db.relationship("User", backref="announcements")
