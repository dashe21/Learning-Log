"""
Main routes for Learning Log application
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Topic

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing recent topics and entries"""
    topics = Topic.query.filter_by(user_id=current_user.id).order_by(Topic.date_created.desc()).limit(5).all()
    return render_template('dashboard.html', topics=topics)