import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app import db
from app.models import User, AuditLog

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    required = ["email", "password", "first_name", "last_name", "role"]
    if not all(data.get(f) for f in required):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    role_name = data["role"].capitalize()
    if role_name not in ("Admin", "Teacher", "Student", "Parent"):
        return jsonify({"error": "Invalid role"}), 400

    from app.models import Role
    role = Role.query.filter_by(name=role_name).first()
    user = User(
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone_number=data.get("phone_number"),
        role_id=role.id,
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    log = AuditLog(
        actor_id=user.id,
        action="Account created",
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        metadata_json=json.dumps({"role": role_name}),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account deactivated"}), 403

    from flask_jwt_extended import create_access_token
    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()})


@auth_bp.route("/me", methods=["GET"])
def me():
    from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
    verify_jwt_in_request()
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    return jsonify(user.to_dict())
