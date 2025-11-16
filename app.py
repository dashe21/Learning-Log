"""
Learning Log Flask Application
A web app for tracking learning topics and entries
"""

from flask import Flask
from flask_login import LoginManager
import os

# Import db from models to avoid circular imports
from models import db

# Initialize Flask extensions
login_manager = LoginManager()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration - handle both local and Docker environments
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and database_url.startswith('sqlite:////app/'):
        # Docker SQLite path detected, but we're running locally - convert to local path
        app.logger.info("Detected Docker SQLite path, converting for local development")
        instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        db_path = os.path.join(instance_dir, 'learning_log.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    elif database_url:
        # Use explicitly set DATABASE_URL (PostgreSQL or other)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # No DATABASE_URL set - use local development default
        instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        db_path = os.path.join(instance_dir, 'learning_log.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Production settings
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Configure security settings
    from security import configure_app_security
    configure_app_security(app)
    
    # Import models
    from models import User, Topic, Entry, Tag, Category
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.topics import topics_bp
    from routes.search import search_bp
    from routes.theme import theme_bp
    from routes.analytics import analytics_bp
    from routes.tags import tags_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(topics_bp, url_prefix='/topics')
    app.register_blueprint(search_bp)
    app.register_blueprint(theme_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(tags_bp)
    
    # Create database tables - only if database is accessible
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Could not create database tables during startup: {e}")
            app.logger.warning("Database tables will need to be created manually or on first request")
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Use port 5001 to avoid conflicts
    app.run(debug=True, port=5000)