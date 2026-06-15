from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.finance.models import Invoice, Payment, Transaction, FeeStructure
from app.models import User, AuditLog

finance_bp = Blueprint("finance", __name__)


def role_required(*roles):
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    if user.role.name not in roles:
        return False, "Forbidden", user
    return True, None, user


@finance_bp.route("/invoices", methods=["GET"])
@jwt_required()
def list_invoices():
    ok, err, _ = role_required("Admin", "Parent", "Student")
    if not ok:
        return jsonify({"error": err}), 403
    uid = int(get_jwt_identity())
    user = User.query.get_or_404(uid)
    q = Invoice.query
    if user.role.name == "Parent":
        children = [c.id for c in user.children]
        q = q.filter(Invoice.student_id.in_(children))
    status = request.args.get("status")
    if status:
        q = q.filter_by(status=status)
    invoices = q.limit(100).all()
    out = []
    for inv in invoices:
        out.append({
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "student_name": inv.student.user.full_name if inv.student and inv.student.user else "",
            "amount": inv.amount,
            "paid_amount": inv.paid_amount,
            "balance": inv.balance,
            "due_date": inv.due_date.isoformat() if inv.due_date else None,
            "status": inv.status,
            "term": inv.term,
            "academic_year": inv.academic_year,
        })
    return jsonify(out)


@finance_bp.route("/invoices", methods=["POST"])
@jwt_required()
def create_invoice():
    ok, err, actor = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    invoice = Invoice(
        student_id=data.get("student_id"),
        invoice_number=f"INV-{db.func.coalesce(db.func.max(Invoice.id), 0) + 1:06d}",
        amount=data.get("amount"),
        term=data.get("term"),
        academic_year=data.get("academic_year"),
        due_date=data.get("due_date"),
        description=data.get("description"),
        fee_structure_id=data.get("fee_structure_id"),
    )
    db.session.add(invoice)
    db.session.commit()
    AuditLog.log(actor.id, f"Created invoice {invoice.invoice_number}", "Invoice", invoice.id)
    return jsonify({"id": invoice.id, "invoice_number": invoice.invoice_number}), 201


@finance_bp.route("/payments", methods=["POST"])
@jwt_required()
def record_payment():
    ok, err, actor = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    invoice = Invoice.query.get_or_404(data.get("invoice_id"))
    payment = Payment(
        invoice_id=invoice.id,
        amount=data.get("amount"),
        method=data.get("method", "Cash"),
        reference=data.get("reference"),
        mpesa_code=data.get("mpesa_code"),
        mpesa_phone=data.get("mpesa_phone"),
        note=data.get("note"),
        received_by_id=actor.id,
    )
    db.session.add(payment)
    db.session.flush()
    invoice.paid_amount = (invoice.paid_amount or 0) + payment.amount
    if invoice.paid_amount >= invoice.amount:
        invoice.status = "Paid"
    elif invoice.paid_amount > 0:
        invoice.status = "Partially Paid"
    tx = Transaction(
        invoice_id=invoice.id,
        payment_id=payment.id,
        type="income",
        category="School Fees",
        amount=payment.amount,
        description=f"Payment for {invoice.invoice_number}",
        reference=payment.reference or payment.mpesa_code,
    )
    db.session.add(tx)
    db.session.commit()
    AuditLog.log(actor.id, f"Recorded payment {payment.amount} for {invoice.invoice_number}", "Payment", payment.id)
    return jsonify({"id": payment.id, "balance": invoice.balance}), 201


@finance_bp.route("/payments", methods=["GET"])
@jwt_required()
def list_payments():
    ok, err, _ = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    payments = Payment.query.limit(100).all()
    out = []
    for p in payments:
        out.append({
            "id": p.id,
            "invoice_number": p.invoice.invoice_number if p.invoice else "",
            "amount": p.amount,
            "method": p.method,
            "reference": p.reference,
            "mpesa_code": p.mpesa_code,
            "paid_at": p.paid_at.isoformat() if p.paid_at else None,
            "received_by": p.received_by.full_name if p.received_by else "",
        })
    return jsonify(out)


@finance_bp.route("/transactions", methods=["GET"])
@jwt_required()
def list_transactions():
    ok, err, _ = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    q = Transaction.query
    tx_type = request.args.get("type")
    if tx_type:
        q = q.filter_by(type=tx_type)
    txs = q.order_by(Transaction.created_at.desc()).limit(100).all()
    out = []
    for t in txs:
        out.append({
            "id": t.id,
            "type": t.type,
            "category": t.category,
            "amount": t.amount,
            "description": t.description,
            "reference": t.reference,
            "created_at": t.created_at.isoformat(),
        })
    return jsonify(out)


@finance_bp.route("/receipts/<int:payment_id>", methods=["GET"])
@jwt_required()
def get_receipt(payment_id):
    ok, err, _ = role_required("Admin", "Parent", "Student")
    if not ok:
        return jsonify({"error": err}), 403
    payment = Payment.query.get_or_404(payment_id)
    return jsonify({
        "receipt_number": f"RCP-{payment.id:08d}",
        "payment": {
            "id": payment.id,
            "amount": payment.amount,
            "method": payment.method,
            "reference": payment.reference,
            "mpesa_code": payment.mpesa_code,
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        },
        "invoice": {
            "invoice_number": payment.invoice.invoice_number if payment.invoice else "",
            "student_name": payment.invoice.student.user.full_name if payment.invoice and payment.invoice.student and payment.invoice.student.user else "",
            "amount": payment.invoice.amount if payment.invoice else 0,
            "balance": payment.invoice.balance if payment.invoice else 0,
        },
    })


@finance_bp.route("/fee-structures", methods=["GET"])
@jwt_required()
def list_fee_structures():
    ok, err, _ = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    items = FeeStructure.query.limit(100).all()
    return jsonify([{
        "id": f.id,
        "name": f.name,
        "grade_level": f.grade_level,
        "term": f.term,
        "academic_year": f.academic_year,
        "amount": f.amount,
        "is_mandatory": f.is_mandatory,
    } for f in items])


@finance_bp.route("/fee-structures", methods=["POST"])
@jwt_required()
def create_fee_structure():
    ok, err, actor = role_required("Admin")
    if not ok:
        return jsonify({"error": err}), 403
    data = request.get_json() or {}
    fs = FeeStructure(
        name=data.get("name"),
        grade_level=data.get("grade_level"),
        term=data.get("term"),
        academic_year=data.get("academic_year"),
        amount=data.get("amount"),
        currency=data.get("currency", "KES"),
        is_mandatory=data.get("is_mandatory", True),
        description=data.get("description"),
    )
    db.session.add(fs)
    db.session.commit()
    AuditLog.log(actor.id, f"Created fee structure {fs.name}", "FeeStructure", fs.id)
    return jsonify({"id": fs.id, "name": fs.name}), 201
