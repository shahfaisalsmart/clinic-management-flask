from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from src.config import Config
from src.common.database import db
from src.admin.models import Department, DoctorProfile
from src.appointments.models import DoctorAvailability, Appointment 
from src.auth.models import User, Role

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #initialize the database & migrations
    db.init_app(app)
    Migrate(app, db)


    #initialize JWT manager
    JWTManager(app)

    #blueprint register below
    from src.auth.routes import auth_bp
    from src.admin.routes import admin_bp
    from src.doctor.routes import doctor_bp
    from src.member.routes import member_bp
    from src.appointments.routes import appointments_bp
    from src.reimbursement.routes import reimburse_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(reimburse_bp)
    

    @app.route('/')
    def index():
        return {"message" : "Welcome to the Clinic Management Backend system"}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)



