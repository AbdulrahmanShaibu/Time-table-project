import os
from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from .imports import db, login_manager
from .config import Config



def create_app(config_object=None):
    # Load environment variables from .env if it exists
    if os.path.exists(".env"):
        load_dotenv(".env")

    # Initialize Flask app
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    # Import and register blueprints
    from .routes import main_bp
    from .api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # CLI command to create sample data
    @app.cli.command("create-sample-data")
    def create_sample():
        """Create demo school, admin, and default timetable template."""
        from .models import School, User, PeriodTemplate
        with app.app_context():
            if School.query.count() == 0:
                school = School(
                    name=app.config.get("DEFAULT_SCHOOL_NAME", "Maahad Istiqama"),
                    timezone=app.config.get("DEFAULT_TIMEZONE", "Africa/Dar_es_Salaam")
                )
                db.session.add(school)
                db.session.commit()

            if User.query.count() == 0:
                admin = User(
                    email=app.config.get("ADMIN_EMAIL", "admin@example.com"),
                    full_name="admin",
                    role="admin"
                )
                admin.set_password(app.config.get("ADMIN_PASSWORD", "admin123"))
                db.session.add(admin)
                db.session.commit()

            if PeriodTemplate.query.count() == 0:
                template = PeriodTemplate(
                    school_id=1,
                    name="Standard (Mon–Fri, 6 periods)",
                    days_per_week=5,
                    periods_per_day=6,
                    break_after_period=3
                )
                db.session.add(template)
                db.session.commit()

            print("✅ Sample data created successfully!")

    return app


# Add a user loader function
from app.imports import login_manager
from app.models import User  # Your User model

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))