from marshmallow import Schema, fields, validate

class MemberUpdateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
