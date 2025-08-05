"""
Desktop specific configuration for AI Blogging Studio
"""
import os
import sqlite3
import tempfile
from pathlib import Path

# Desktop app specific paths
DESKTOP_APP_DIR = Path(__file__).parent.parent
DATA_DIR = DESKTOP_APP_DIR / "data"
DB_DIR = DATA_DIR / "database"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

# Use SQLite for desktop version instead of PostgreSQL
DESKTOP_DATABASE_PATH = DB_DIR / "ai_blogging_studio.db"

# Desktop environment variables
os.environ['DATABASE_URL'] = f'sqlite:///{DESKTOP_DATABASE_PATH}'
os.environ['SESSION_SECRET'] = 'desktop-ai-blogging-studio-secret-key-2024'

def initialize_desktop_database():
    """Initialize SQLite database for desktop app"""
    if not DESKTOP_DATABASE_PATH.exists():
        print(f"Creating desktop database at: {DESKTOP_DATABASE_PATH}")
        # Database will be created automatically by SQLAlchemy
    return str(DESKTOP_DATABASE_PATH)