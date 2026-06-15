from datetime import datetime, date
from app import db


class DashboardMetric(db.Model):
    __tablename__ = "dashboard_metrics"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Numeric(12, 2), default=0)
    value_text = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(255), nullable=False)
    target_type = db.Column(db.String(100))
    target_id = db.Column(db.Integer)
    metadata_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    actor = db.relationship("User", backref="activity_logs")


class SchoolStats(db.Model):
    __tablename__ = "school_stats"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Numeric(12, 2), default=0)
    value_text = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get(key, default=None):
        s = SchoolStats.query.filter_by(key=key).first()
        if not s:
            return default if default is not None else 0
        return s.value if s.value is not None else (default if default is not None else 0)

    @staticmethod
    def set(key, value):
        s = SchoolStats.query.filter_by(key=key).first()
        if not s:
            s = SchoolStats(key=key)
            db.session.add(s)
        s.value = value
        db.session.commit()
