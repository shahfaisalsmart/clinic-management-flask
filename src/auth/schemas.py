from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role_name = fields.Str(required=True, validate=validate.OneOf(["Admin","Doctor","Member"]))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


