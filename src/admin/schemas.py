from marshmallow import Schema, fields, validate

class DepartmentSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str(required=False, validate=validate.Length(max=255))

class DoctorOnboardSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    specialization = fields.Str(required=True)
    qualification = fields.Str(required=True)
    department_id = fields.Int(required=False) # Shuru me bina department ke bhi onboard ho sakta hai

class AssignDoctorSchema(Schema):
    doctor_id = fields.Int(required=True)
    department_id = fields.Int(required=True)

