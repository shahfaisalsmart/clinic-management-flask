from marshmallow import Schema, fields, validate

class DoctorUpdateSchema(Schema):
    # Industry Standard: Update schema mein saare fields required=False hote hain
    name = fields.Str(required=False, validate=validate.Length(min=2, max=100))
    specialization = fields.Str(required=False, validate=validate.Length(min=2, max=100))
    qualification = fields.Str(required=False, validate=validate.Length(min=2, max=100))

