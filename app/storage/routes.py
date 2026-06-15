from flask import Blueprint, jsonify, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

storage_bp = Blueprint("storage", __name__)


@storage_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if not user.has_permission("manage_users"):
        return jsonify({"error": "Forbidden"}), 403
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".docx", ".xlsx", ".zip"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if f".{ext}" not in allowed:
        return jsonify({"error": "File type not allowed"}), 400
    import time
    filename = f"{int(time.time())}_{file.filename}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    file.save(upload_dir + "/" + filename)
    return jsonify({"url": "/static/uploads/" + filename, "filename": filename})


@storage_bp.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
