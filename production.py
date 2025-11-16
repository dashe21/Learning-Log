"""
Production-ready Flask application with Gunicorn
"""

import os
import sys
sys.path.insert(0, '/app')

# Import the application factory and database
from app import create_app
from models import db

# Create the application instance
application = create_app()

# Initialize application context and create tables
with application.app_context():
    # Create database tables
    db.create_all()
    print("Database tables created successfully!")

if __name__ == "__main__":
    # For development only - use gunicorn for production
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    application.run(host=host, port=port, debug=False)