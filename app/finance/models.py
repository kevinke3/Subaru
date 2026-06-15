from datetime import datetime
from decimal import Decimal
from app import db


class Invoice(db.Model):
    __tablename__ = "invoices"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), default=0)
    currency = db.Column(db.String(10), default="KES")
    term = db.Column(db.String(50))
    academic_year = db.Column(db.String(20))
    fee_structure_id = db.Column(db.Integer, db.ForeignKey("fee_structures.id"))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(30), default="Unpaid")
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship("Student", backref="invoices")
    fee_structure = db.relationship("FeeStructure", backref="invoices")
    payments = db.relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

    @property
    def balance(self):
        return Decimal(str(self.amount)) - Decimal(str(self.paid_amount or 0))


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(30), default="Cash")
    reference = db.Column(db.String(100), index=True)
    mpesa_code = db.Column(db.String(50))
    mpesa_phone = db.Column(db.String(20))
    note = db.Column(db.Text)
    received_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoice = db.relationship("Invoice", back_populates="payments")
    received_by = db.relationship("User", backref="payments_received")


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"))
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"))
    type = db.Column(db.String(20), default="income")
    category = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    reference = db.Column(db.String(100))
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoice = db.relationship("Invoice")
    payment = db.relationship("Payment")
    created_by = db.relationship("User", backref="transactions")


class FeeStructure(db.Model):
    __tablename__ = "fee_structures"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.String(50))
    term = db.Column(db.String(50))
    academic_year = db.Column(db.String(20))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default="KES")
    is_mandatory = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
