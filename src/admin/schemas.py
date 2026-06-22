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
   #department_id = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, error="Department ID must be greater than 0")) # Shuru me bina department ke bhi onboard ho sakta hai

class AssignDoctorSchema(Schema):
    doctor_id = fields.Int(required=True)
    department_id = fields.Int(required=True, validate=validate.Range(min=1, error="Dept ID must be greater than 0"))



