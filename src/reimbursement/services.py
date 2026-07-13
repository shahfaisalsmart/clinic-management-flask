from src.reimbursement.repositories import ReimbursementRepository
from src.appointments.models import Appointment # Future claims tracking linkage ke liye
from src.reimbursement.models import UserInsurance, MedicalRecord, ReimbursementClaim
from src.common.database import db
from dateutil.relativedelta import relativedelta #  Perfect Month calculation ke liye
from datetime import datetime

class ReimbursementService:

    def __init__(self):
        self.reimburse_repo = ReimbursementRepository()

    def launch_new_product(self, data: dict):
        if self.reimburse_repo.get_product_by_name(data['name']):
            return {"error": "Is naam ka insurance product pehle se exists karta hai!"}, 400
            
        product = self.reimburse_repo.create_insurance_product(data)
        return {
            "status": "SUCCESS",
            "message": f"Insurance product '{product.name}' successfully launched by Health Provider!",
            "product_id": product.id
        }, 201

    def get_admin_comprehensive_dashboard(self):
        products = self.reimburse_repo.get_all_products_with_metrics()
        
        dashboard_data = []
        for p in products:
            # Har product ke niche kitne members enrolled hain unka count aur metrics calculation
            total_purchases = len(p.user_insurances)
            
            # Realtime metrics extraction
            active_enrolled_users = []
            for ui in p.user_insurances:
                active_enrolled_users.append({
                    "user_insurance_id": ui.id,
                    "patient_name": ui.member.name if ui.member else "Unknown Patient",
                    "purchase_date": ui.purchase_date.strftime("%Y-%m-%d"),
                    "expiry_date": ui.expiry_date.strftime("%Y-%m-%d"),
                    "initial_limit": ui.initial_coverage,
                    "remaining_balance": ui.remaining_coverage, # Jaisa aapne kaha deduction ke baad bacha paisa
                    "reimbursement_history": [] # 🚀 Note: Jab claims module likhenge, ye automatic fill hoga!
                })

            dashboard_data.append({
                "product_id": p.id,
                "product_name": p.name,
                "cost_price": p.product_cost,
                "allowed_coverage_limit": p.total_coverage,
                "covered_benefits": p.product_benefit,
                "claim_allowed_within_days": f"{p.claim_window_days} days post-treatment",
                "plan_validity": f"{p.validity_months} Months",
                "total_active_subscribers": total_purchases,
                "enrolled_patients_details": active_enrolled_users
            })
            
        return {
            "provider_organization": "Clinic Management Health Administration",
            "total_insurance_products_launched": len(products),
            "products_registry": dashboard_data
        }, 200
    
    #------------------- PATIENT LOGICS-----------------------------------------
    def patient_universal_product_search(self, search_query: str):
        products = self.reimburse_repo.search_active_insurance_products(search_query)
        if not products:
            return {"message": "Health Provider ki taraf se aisa koi insurance product nahi mila!"}, 404

        result = []
        for p in products:
            result.append({
                "product_id": p.id,
                "name": p.name,
                "cost": p.product_cost,
                "coverage_limit": p.total_coverage,
                "covered_treatments": p.product_benefit,
                "claim_window": f"{p.claim_window_days} days post-treatment",
                "validity_period": f"{p.validity_months} Months"
            })
        return result, 200

    def opt_insurance_product(self, member_id: int, data: dict):
        product_id = data['product_id']
        
        # 1. Check karo ki product valid hai ya nahi
        product = self.reimburse_repo.get_product_by_id(product_id)
        if not product:
            return {"error": "Invalid Product ID! Is naam ka koi plan nahi mila."}, 404

        # 2. CHECK: Same product ID dobara kharidne se roko agar wo active hai
        existing_active = self.reimburse_repo.get_active_user_insurance(member_id, product_id)
        if existing_active:
            expiry_str = existing_active.expiry_date.strftime("%Y-%m-%d")
            return {
                "error": f"Aapne yeh insurance plan already le rakha hai! Yeh product {expiry_str} tak valid hai, tab tak aap naya plan opt nahi kar sakte."
            }, 400

        # 3. Expiry Date and Coverage Limits mapping
        current_time = datetime.utcnow()
        calculated_expiry = current_time + relativedelta(months=product.validity_months)

        new_opt = UserInsurance(
            member_id=member_id,
            product_id=product.id,
            purchase_date=current_time,
            expiry_date=calculated_expiry,
            initial_coverage=product.total_coverage,
            remaining_coverage=product.total_coverage # Shuru me dono total same rahenge
        )

        self.reimburse_repo.create_user_insurance(new_opt)
        return {
            "status": "SUCCESS",
            "message": f"Kamyabi ke sath aapne '{product.name}' plan opt kar liya hai! Aapke dashboard par countdown shuru ho gaya hai.",
            "insurance_details": {
                "user_insurance_id": new_opt.id,
                "total_coverage": new_opt.initial_coverage,
                "expiry_date": calculated_expiry.strftime("%Y-%m-%d")
            }
        }, 201

    def get_patient_insurance_dashboard(self, member_id: int):
        user_plans = self.reimburse_repo.get_member_insurance_dashboard_data(member_id)
        if not user_plans:
            return {"message": "Aapne abhi tak koi health insurance product opt nahi kiya hai!"}, 200

        dashboard_registry = []
        current_time = datetime.utcnow()

        for up in user_plans:
            # REALTIME COUNTDOWN GENERATOR: "X months, Y days"
            if up.expiry_date > current_time:
                diff = relativedelta(up.expiry_date, current_time)
                countdown_string = f"{diff.months} months, {diff.days} days remaining"
                status_flag = "ACTIVE"
            else:
                countdown_string = "0 months, 0 days remaining (EXPIRED)"
                status_flag = "EXPIRED"

            dashboard_registry.append({
                "user_insurance_id": up.id,
                "status": status_flag,
                "product_details": {
                    "product_id": up.product.id,
                    "name": up.product.name,
                    "covered_benefits": up.product.product_benefit,
                    "claim_window_limit": f"{up.product.claim_window_days} days"
                },
                "financial_metrics": {
                    "total_coverage": up.initial_coverage,
                    "remaining_balance": up.remaining_coverage # Yeh live treatment claims deduct hone par update hoga!
                },
                "timeline": {
                    "purchased_on": up.purchase_date.strftime("%Y-%m-%d"),
                    "expires_on": up.expiry_date.strftime("%Y-%m-%d"),
                    "live_countdown": countdown_string
                }
            })

        return {
            "patient_id": member_id,
            "total_enrolled_insurance_plans": len(user_plans),
            "my_insurance_portfolio": dashboard_registry
        }, 200
    
    
    # DOCTOR PIPELINE: Create Treatment Receipt
    def doctor_create_medical_record(self, doctor_id: int, data: dict):
        new_record = MedicalRecord(
            doctor_id=doctor_id,
            member_id=data['member_id'],
            treatment_name=data['treatment_name'],
            treatment_cost=data['treatment_cost'],
            venue_address=data['venue_address']
        )
        self.reimburse_repo.create_medical_record(new_record)
        return {
            "status": "SUCCESS",
            "message": "Patient ka medical record aur digital prescription securely log ho gaya hai!",
            "medical_record_id": new_record.id
        }, 201

    # PATIENT PIPELINE: Search & File Insurance Claim
    def patient_search_medical_records(self, member_id: int, query: str):
        records = self.reimburse_repo.search_member_medical_records(member_id, query)
        if not records:
            return {"message": "Is query se match karta hua aapka koi medical record nahi mila."}, 404
        
        return [{
            "medical_record_id": r.id,
            "treatment": r.treatment_name,
            "cost": r.treatment_cost,
            "date": r.treatment_date.strftime("%Y-%m-%d"),
            "clinic": r.venue_address,
            "doctor": r.doctor.name if r.doctor else "Unknown Doctor",
            "claim_status": r.claim.status if r.claim else "NOT_FILED"
        } for r in records], 200

    def patient_file_reimbursement_claim(self, member_id: int, data: dict):
        record = self.reimburse_repo.get_medical_record_by_id(data['medical_record_id'])
        
        # 1. Validation check
        if not record or record.member_id != member_id:
            return {"error": "Invalid Medical Record ID matching this patient profile!"}, 400
            
        if self.reimburse_repo.get_claim_by_medical_record(record.id):
            return {"error": "Is medical record par already reimbursement file kiya ja chuka hai!"}, 400

        new_claim = ReimbursementClaim(
            user_insurance_id=data['user_insurance_id'],
            medical_record_id=record.id,
            status="PENDING"
        )
        self.reimburse_repo.create_claim(new_claim)
        return {
            "status": "SUCCESS",
            "message": "Reimbursement claim successfully Health Provider ko forward kar diya gaya hai!",
            "claim_id": new_claim.id
        }, 201

    # ADMIN/HEALTH PROVIDER PIPELINE: Rule Engine Verification & Deduction
    def admin_process_reimbursement_claim(self, claim_id: int, data: dict):
        claim = self.reimburse_repo.get_claim_by_id(claim_id)
        if not claim:
            return {"error": "Claim not found!"}, 404
        if claim.status != "PENDING":
            return {"error": f"Yeh claim already {claim.status} ho chuka hai!"}, 400

        if data['action'] == "REJECT":
            claim.status = "REJECTED"
            claim.admin_remarks = data.get('remarks', "Rejected by provider.")
            claim.processed_at = datetime.utcnow()
            self.reimburse_repo.commit_changes()
            return {"status": "PROCESSED", "message": "Claim successfully REJECTED and updated on dashboard."}, 200

        # ----  CORE INSURANCE CHECKS (APPROVE WORKFLOW) ----
        insurance = claim.user_insurance
        record = claim.medical_record

        # Check 1: Expiry verification
        if insurance.expiry_date < datetime.utcnow():
            claim.status = "REJECTED"
            claim.admin_remarks = "Policy tenure has expired!"
            self.reimburse_repo.commit_changes()
            return {"error": "Insurance scheme expire ho chuki hai! Claim auto-reject ho gaya."}, 400

        # Check 2: Benefit/Treatment Coverage Verification
        if record.treatment_name not in insurance.product.product_benefit:
            claim.status = "REJECTED"
            claim.admin_remarks = f"Treatment '{record.treatment_name}' is not covered under this product plan."
            self.reimburse_repo.commit_changes()
            return {"error": f"Aapke selected insurance pack me '{record.treatment_name}' cover nahi hai! Claim auto-reject ho gaya."}, 400

        # Check 3: Insufficient Balance Verification
        if insurance.remaining_coverage < record.treatment_cost:
            return {
                "error": "insufficient balance",
                "message": f"Insurance package wallet me sirf ₹{insurance.remaining_coverage} bache hain, par bill ₹{record.treatment_cost} ka hai!"
            }, 400

        # Everything is valid -> Deduct & Save
        insurance.remaining_coverage -= record.treatment_cost
        claim.status = "APPROVED"
        claim.admin_remarks = data.get('remarks', "All checks passed. Claim settled successfully!")
        claim.processed_at = datetime.utcnow()
        
        self.reimburse_repo.commit_changes()
        return {
            "status": "SETTLED",
            "message": "Claim approved seamlessly! Deducted amount from subscriber account wallet.",
            "remaining_policy_balance": insurance.remaining_coverage
        }, 200