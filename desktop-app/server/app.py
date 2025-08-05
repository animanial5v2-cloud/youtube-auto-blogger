import os
import logging
import sys

# Desktop app configuration
try:
    from desktop_config import initialize_desktop_database
    initialize_desktop_database()
    print("Desktop app mode: Using SQLite database")
    DESKTOP_MODE = True
except ImportError:
    print("Web app mode: Using PostgreSQL database")
    DESKTOP_MODE = False

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "desktop-app-secret-key-2024")

# Only use ProxyFix for web deployment
if not DESKTOP_MODE:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if DESKTOP_MODE and database_url and database_url.startswith("sqlite"):
    # SQLite configuration for desktop
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }
else:
    # PostgreSQL configuration for web
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "postgresql://localhost/ai_blogging_studio"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models and routes
    import models
    import routes
    
    # Create all tables
    db.create_all()
