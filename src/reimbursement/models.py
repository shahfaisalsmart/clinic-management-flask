from src.common.database import db
from datetime import datetime

class InsuranceProduct(db.Model):
    __tablename__ = 'insurance_products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product_cost = db.Column(db.Float, nullable=False)          # Product ki price (e.g., 5000)
    total_coverage = db.Column(db.Float, nullable=False)        # Total kitne tak ka reimbursement mil sakta hai (e.g., 50000)
    product_benefit = db.Column(db.JSON, nullable=False)         # Covered treatments list (e.g., ["Root Canal", "Consultation"])
    claim_window_days = db.Column(db.Integer, nullable=False)   # Treatment ke kitne din ke andar claim file karna zaroori hai
    validity_months = db.Column(db.Integer, nullable=False)     # Insurance khareedne ke baad kitne mahine valid rahega (e.g., 12)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_insurances = db.relationship('UserInsurance', backref='product', lazy=True)

    def __repr__(self):
        return f"<InsuranceProduct {self.name}>"


class UserInsurance(db.Model):
    __tablename__ = 'user_insurances'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('insurance_products.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=False)
    
    # Remaining money track karne ke liye dynamic variables
    initial_coverage = db.Column(db.Float, nullable=False)
    remaining_coverage = db.Column(db.Float, nullable=False)     # E.g., 1000 - 80 = 920 bacha

    # Relationship to Patient (User) mapping
    member = db.relationship('User', foreign_keys=[member_id])

    def __repr__(self):
        return f"<UserInsurance Member:{self.member_id} Product:{self.product_id}>"
    
class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    treatment_name = db.Column(db.String(100), nullable=False)   # E.g., "Root Canal"
    treatment_cost = db.Column(db.Float, nullable=False)         # E.g., 1000.0
    treatment_date = db.Column(db.Date, default=datetime.utcnow().date)
    venue_address = db.Column(db.String(255), nullable=False)    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships mapping
    doctor = db.relationship('User', foreign_keys=[doctor_id])
    member = db.relationship('User', foreign_keys=[member_id])
    claim = db.relationship('ReimbursementClaim', backref='medical_record', uselist=False, lazy=True)

    def __repr__(self):
        return f"<MedicalRecord {self.id} - {self.treatment_name}>"


class ReimbursementClaim(db.Model):
    __tablename__ = 'reimbursement_claims'

    id = db.Column(db.Integer, primary_key=True)
    user_insurance_id = db.Column(db.Integer, db.ForeignKey('user_insurances.id'), nullable=False)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False, unique=True)
    status = db.Column(db.String(20), default="PENDING")         # PENDING, APPROVED, REJECTED
    admin_remarks = db.Column(db.String(255), nullable=True)     # Approval/Rejection ka reason
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_insurance = db.relationship('UserInsurance', backref='claims', lazy=True)

    def __repr__(self):
        return f"<Claim {self.id} - Status: {self.status}>"