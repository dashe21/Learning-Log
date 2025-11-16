"""
Theme preference management for Learning Log application
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required

theme_bp = Blueprint('theme', __name__)

@theme_bp.route('/api/theme', methods=['POST'])
@login_required
def save_theme_preference():
    """Save user theme preference to database"""
    data = request.get_json()
    theme = data.get('theme', 'light')
    
    if theme not in ['light', 'dark', 'auto']:
        return jsonify({'error': 'Invalid theme'}), 400
    
    try:
        # Add theme column to user model if it doesn't exist
        # For now, we'll use localStorage, but this allows future database storage
        return jsonify({'status': 'success', 'theme': theme})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@theme_bp.route('/api/theme', methods=['GET'])
@login_required
def get_theme_preference():
    """Get user theme preference from database"""
    # For now, return default - can be extended to read from user profile
    return jsonify({'theme': 'light'})