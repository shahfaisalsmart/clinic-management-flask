from src.reimbursement.models import InsuranceProduct, UserInsurance, MedicalRecord, ReimbursementClaim
from src.common.database import db
from sqlalchemy import or_

class ReimbursementRepository:

    def get_product_by_name(self, name: str):
        return InsuranceProduct.query.filter_by(name=name).first()

    def create_insurance_product(self, data: dict):
        product = InsuranceProduct(
            name=data['name'],
            product_cost=data['product_cost'],
            total_coverage=data['total_coverage'],
            product_benefit=data['product_benefit'],
            claim_window_days=data['claim_window_days'],
            validity_months=data['validity_months']
        )
        db.session.add(product)
        db.session.commit()
        return product

    def get_all_products_with_metrics(self):
        # Admin dashboard ke liye saare plans fetch karenge
        return InsuranceProduct.query.order_by(InsuranceProduct.created_at.desc()).all()
    
    def search_active_insurance_products(self, search_query: str):
        """SINGLE LINE UNIVERSAL SEARCH FOR INSURANCE PRODUCTS"""
        return InsuranceProduct.query.filter(or_(InsuranceProduct.name.ilike(f"%{search_query}%"), 
                                                 InsuranceProduct.product_benefit.cast(db.String).ilike(f"%{search_query}%"), 
                                                 InsuranceProduct.total_coverage.cast(db.String).ilike(f"%{search_query}%"))).all()

    def get_product_by_id(self, product_id: int):
        return InsuranceProduct.query.get(product_id)

    def get_active_user_insurance(self, member_id: int, product_id: int):
        """Check karega ki kya patient ke paas ye product already active hai (not expired)"""
        from datetime import datetime
        return UserInsurance.query.filter(
            UserInsurance.member_id == member_id,
            UserInsurance.product_id == product_id,
            UserInsurance.expiry_date > datetime.utcnow()
        ).first()

    def create_user_insurance(self, user_insurance_obj):
        db.session.add(user_insurance_obj)
        db.session.commit()
        return user_insurance_obj

    def get_member_insurance_dashboard_data(self, member_id: int):
        """Patient ke saare active aur past insurance plans dhoond ke layega"""
        return UserInsurance.query.filter_by(member_id=member_id).order_by(UserInsurance.purchase_date.desc()).all()
    
    def create_medical_record(self, record_obj):
        db.session.add(record_obj)
        db.session.commit()
        return record_obj

    def get_medical_record_by_id(self, record_id: int):
        return MedicalRecord.query.get(record_id)

    def search_member_medical_records(self, member_id: int, query: str):
        """SINGLE LINE UNIVERSAL SEARCH FOR MEMBER'S MEDICAL RECORDS"""
        return MedicalRecord.query.filter(MedicalRecord.member_id == member_id).filter(MedicalRecord.treatment_name.ilike(f"%{query}%")).all()

    def get_claim_by_medical_record(self, record_id: int):
        return ReimbursementClaim.query.filter_by(medical_record_id=record_id).first()

    def create_claim(self, claim_obj):
        db.session.add(claim_obj)
        db.session.commit()
        return claim_obj

    def get_claim_by_id(self, claim_id: int):
        return ReimbursementClaim.query.get(claim_id)

    def commit_changes(self):
        db.session.commit()