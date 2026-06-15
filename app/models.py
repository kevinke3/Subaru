import json
from datetime import datetime, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.relationship("Permission", secondary="role_permissions", backref="roles")

    @staticmethod
    def get_or_create(name):
        role = Role.query.filter_by(name=name).first()
        if role:
            return role, False
        role = Role(name=name)
        db.session.add(role)
        db.session.commit()
        return role, True


class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    @staticmethod
    def get_or_create(name):
        perm = Permission.query.filter_by(name=name).first()
        if perm:
            return perm, False
        perm = Permission(name=name)
        db.session.add(perm)
        db.session.commit()
        return perm, True


role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    avatar_url = db.Column(db.String(500))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = db.relationship("Role", backref="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_permission(self, name):
        return any(p.name == name for p in self.role.permissions)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role.name if self.role else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat(),
        }


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    admission_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    address = db.Column(db.Text)
    grade_level = db.Column(db.String(20))
    enrollment_date = db.Column(db.Date)
    parent_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    emergency_contact = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    medical_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="student_profile", foreign_keys=[user_id])
    parent = db.relationship("User", backref="children", foreign_keys=[parent_id])


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    employee_number = db.Column(db.String(50), unique=True, index=True)
    qualification = db.Column(db.String(200))
    specialization = db.Column(db.String(200))
    hire_date = db.Column(db.Date)
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="teacher_profile", foreign_keys=[user_id])


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    target_type = db.Column(db.String(100))
    target_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    metadata_json = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    actor = db.relationship("User", backref="audit_logs")

    @staticmethod
    def log(actor_id, action, target_type=None, target_id=None, ip_address=None,
            user_agent=None, metadata_json=None):
        log = AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=json.dumps(metadata_json) if metadata_json is not None else None,
        )
        db.session.add(log)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "actor": self.actor.full_name if self.actor else "System",
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat(),
        }
