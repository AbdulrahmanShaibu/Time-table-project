import os

class Config:
    # Secret key for session encryption
    SECRET_KEY = os.environ.get("SECRET_KEY") or "4a8e2fbd913bb7b0f1a4f85c67943f1e764bc7e53ff2fa54c79c1a123b7bcded"

    # Database configuration (no password for MySQL user)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "mysql+pymysql://school_user:@localhost/school_timetabl_db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default school settings
    DEFAULT_SCHOOL_NAME = "Maahad Istiqama"
    DEFAULT_TIMEZONE = "Africa/Dar_es_Salaam"

    # Default admin credentials
    ADMIN_EMAIL = "admin@example.com"
    ADMIN_PASSWORD = "admin123"
