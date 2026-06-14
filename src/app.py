from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from src.config import Config
from src.common.database import db
from src.admin.models import Department, DoctorProfile  


from src.auth.models import User, Role
from src.admin.models import Department, DoctorProfile

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #initialize the database & migrations
    db.init_app(app)
    Migrate(app, db)

    #custom CLI command --> Roles ki SEEDING karne ke liye
    @app.cli.command("seed-roles")
    def seed_roles():
        roles = ["Admin", "Doctor", "Member"]
        for role_name in roles:
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                new_role = Role(name=role_name)
                db.session.add(new_role)
        db.session.commit()
        print("Roles seeding successful")

    #initialize JWT manager
    JWTManager(app)

    #blueprint register below
    from src.auth.routes import auth_bp
    from src.admin.routes import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    

    @app.route('/')
    def index():
        return {"message" : "Welcome to the Clinic Management Backend system"}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)



