from marshmallow import Schema, fields, validate

class LaunchProductSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    product_cost = fields.Float(required=True, validate=validate.Range(min=1))
    total_coverage = fields.Float(required=True, validate=validate.Range(min=1))
    product_benefit = fields.List(fields.Str(), required=True) # Array of treatments e.g. ["Root Canal"]
    claim_window_days = fields.Integer(required=True, validate=validate.Range(min=1))
    validity_months = fields.Integer(required=True, validate=validate.Range(min=1))

class OptProductSchema(Schema):
    product_id = fields.Integer(required=True, validate=validate.Range(min=1))


class CreateMedicalRecordSchema(Schema):
    member_id = fields.Integer(required=True)
    treatment_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    treatment_cost = fields.Float(required=True, validate=validate.Range(min=1))
    venue_address = fields.Str(required=True, validate=validate.Length(min=5, max=255))

class FileClaimSchema(Schema):
    user_insurance_id = fields.Integer(required=True)
    medical_record_id = fields.Integer(required=True)

class ProcessClaimSchema(Schema):
    action = fields.Str(required=True, validate=validate.OneOf(["APPROVE", "REJECT"]))
    remarks = fields.Str(required=False, validate=validate.Length(max=255))