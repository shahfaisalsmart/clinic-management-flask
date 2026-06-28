from marshmallow import Schema, fields, validate

"""
class AddAvailabilitySchema(Schema):
    venue_id = fields.Int(required=True)
    slot_start = fields.DateTime(required=True) # Format: YYYY-MM-DDTHH:MM:SS
    slot_end = fields.DateTime(required=True)
    #is_home_visit = fields.Boolean(required=False, load_default=False)
    fee = fields.Float(required=True, validate=validate.Range(min=0))
"""
    
class DayScheduleSchema(Schema):
    day_of_week = fields.Str(required=True, validate=validate.OneOf(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    ))
    start_time = fields.Str(required=True, validate=validate.Regexp(r'^\d{2}:\d{2}$')) # e.g., "09:00"
    end_time = fields.Str(required=True, validate=validate.Regexp(r'^\d{2}:\d{2}$'))   # e.g., "17:00"
    slot_duration_mins = fields.Int(load_default=30) # appointment timing length

class UpdateDoctorProfileAndScheduleSchema(Schema):
    venue_address = fields.Str(required=True, validate=validate.Length(min=5))
    start_time = fields.Str(required=True, validate=validate.Regexp(r'^\d{2}:\d{2}$')) # e.g. "16:00"
    end_time = fields.Str(required=True, validate=validate.Regexp(r'^\d{2}:\d{2}$'))   # e.g. "19:00"
    slot_duration_mins = fields.Int(required=True, validate=validate.Range(min=5, max=120))
    fee = fields.Float(required=True, validate=validate.Range(min=0))
    treatment_services = fields.List(fields.Str(), required=True)
    work_on_sunday = fields.Boolean(load_default=False)

class BulkHolidaySchema(Schema):
    """NEW VALIDATOR: Postman se multiple data points parse krne ke liye"""
    holiday_dates = fields.List(
        fields.Str(required=True, validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$')),
        required=True
    )

class BookAppointmentSchema(Schema):
    doctor_id = fields.Int(required=True)
    slot_id = fields.Int(required=True)

class CancelRequestSchema(Schema):
    appointment_id = fields.Int(required=True)
    cancellation_reason = fields.Str(required=True)

class DoctorApproveCancelSchema(Schema):
    appointment_id = fields.Int(required=True)
    action = fields.Str(required=True, validate=validate.OneOf(["APPROVE", "REJECT"]))


# Admin ko doctor ki detail dikhane ke liye
class DoctorDetailSchema(Schema):
    id = fields.Int()
    name = fields.Method("get_doctor_name")
    specialization = fields.Str()

    def get_doctor_name(self, obj):
        # obj yahan DoctorProfile ka instance hoga
        return obj.user.name if obj.user else None

# Admin ko patient ki detail dikhane ke liye
class PatientDetailSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Str()

# Main Response Schema jo dono dashboards use karenge
class CancellationDashboardSchema(Schema):
    appointment_id = fields.Int(attribute="id")
    status = fields.Method("get_status_value")
    token_number = fields.Int()
    cancellation_reason = fields.Str()
    created_at = fields.DateTime()
    
    # Nested fields (Hum context ke hisab se dynamically control karenge)
    doctor_details = fields.Nested(DoctorDetailSchema, attribute="doctor")
    patient_details = fields.Nested(PatientDetailSchema, attribute="patient")

    def get_status_value(self, obj):
        return obj.status.value

# Schemas ke instances initialize karein
cancellation_dashboard_list_schema = CancellationDashboardSchema(many=True)

class AdminAllAppointmentsResponseSchema(Schema):
    appointment_id = fields.Int(attribute="id")
    token_number = fields.Int()
    status = fields.Method("get_status_value")
    cancellation_reason = fields.Str()
    cancelled_at = fields.DateTime()
    created_at = fields.DateTime()
    
    # Custom fields jo hum query join ke baad dynamically populate karenge
    patient_name = fields.Str()
    doctor_name = fields.Str()

    def get_status_value(self, obj):
        # Enum value ko string me convert karne ke liye
        return obj.status.value if obj.status else None

# Instance initialize karein
admin_all_appointments_list_schema = AdminAllAppointmentsResponseSchema(many=True)

