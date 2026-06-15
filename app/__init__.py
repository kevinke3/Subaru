from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail
import os

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")
mail = Mail()


def create_app():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(__name__,
                template_folder=os.path.join(project_root, "templates"),
                static_folder=os.path.join(project_root, "static"),
                instance_relative_config=True)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "super-secret-classmate-key"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", "sqlite:///" + os.path.join(app.instance_path, "classmate.db")
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "super-secret-classmate-key"),
        UPLOAD_FOLDER=os.path.join(os.path.dirname(__file__), "static", "uploads"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_PORT=int(os.environ.get("MAIL_PORT", 587)),
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
        MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.environ.get("MAIL_DEFAULT_SENDER"),
    )

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    mail.init_app(app)

    with app.app_context():
        from app.models import Role, Permission, User, Teacher, Student
        import app.academics.models as _ac
        import app.attendance.models as _at
        import app.finance.models as _fi
        import app.exams.models as _ex
        import app.messaging.models as _ms
        import app.analytics.models as _an
        import app.notifications.models as _no
        db.create_all()
        from app.models import Role, Permission, User
        for r in ("Admin", "Teacher", "Student", "Parent"):
            Role.get_or_create(name=r)
        perms = [
            "view_dashboard", "manage_users", "manage_students",
            "manage_teachers", "manage_academics", "manage_finance",
            "manage_attendance", "send_messages", "view_reports",
            "manage_settings", "manage_admissions",
            "take_attendance", "grade_assignments", "create_exams",
            "view_children", "pay_fees"
        ]
        for p in perms:
            Permission.get_or_create(name=p)
        db.session.commit()

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    from app.students.routes import students_bp
    app.register_blueprint(students_bp, url_prefix="/api/students")
    from app.teachers.routes import teachers_bp
    app.register_blueprint(teachers_bp, url_prefix="/api/teachers")
    from app.academics.routes import academics_bp
    app.register_blueprint(academics_bp, url_prefix="/api/academics")
    from app.attendance.routes import attendance_bp
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    from app.finance.routes import finance_bp
    app.register_blueprint(finance_bp, url_prefix="/api/finance")
    from app.exams.routes import exams_bp
    app.register_blueprint(exams_bp, url_prefix="/api/exams")
    from app.messaging.routes import messaging_bp
    app.register_blueprint(messaging_bp, url_prefix="/api/messaging")
    from app.notifications.routes import notifications_bp
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    from app.analytics.routes import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    from app.settings.routes import settings_bp
    app.register_blueprint(settings_bp, url_prefix="/api/settings")
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    from app.storage.routes import storage_bp
    app.register_blueprint(storage_bp, url_prefix="/api/storage")

    return app


def create_socketio():
    return socketio
