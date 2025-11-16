"""
Search functionality for Learning Log application
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import Topic, Entry, db
from sqlalchemy import or_

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
@login_required
def search():
    """Search topics and entries"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('topics.index'))
    
    # Search in topics (name and description)
    topic_results = Topic.query.filter(
        Topic.user_id == current_user.id,
        or_(
            Topic.name.contains(query),
            Topic.description.contains(query)
        )
    ).all()
    
    # Search in entries (title and content)
    entry_results = Entry.query.join(Topic).filter(
        Topic.user_id == current_user.id,
        or_(
            Entry.title.contains(query),
            Entry.content.contains(query)
        )
    ).order_by(Entry.date_created.desc()).all()
    
    # Count results
    total_results = len(topic_results) + len(entry_results)
    
    return render_template('search/results.html',
                         query=query,
                         topic_results=topic_results,
                         entry_results=entry_results,
                         total_results=total_results)

@search_bp.route('/search/api')
@login_required
def search_api():
    """API endpoint for search suggestions"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return {'suggestions': []}
    
    # Get topic suggestions
    topics = Topic.query.filter(
        Topic.user_id == current_user.id,
        Topic.name.contains(query)
    ).limit(5).all()
    
    # Get entry suggestions
    entries = Entry.query.join(Topic).filter(
        Topic.user_id == current_user.id,
        Entry.title.contains(query)
    ).limit(5).all()
    
    suggestions = []
    
    # Add topic suggestions
    for topic in topics:
        suggestions.append({
            'type': 'topic',
            'title': topic.name,
            'url': url_for('topics.view', id=topic.id),
            'description': topic.description[:100] + '...' if topic.description and len(topic.description) > 100 else topic.description
        })
    
    # Add entry suggestions
    for entry in entries:
        suggestions.append({
            'type': 'entry',
            'title': entry.title,
            'url': url_for('topics.view', id=entry.topic.id) + f'#entry-{entry.id}',
            'description': f"in {entry.topic.name}"
        })
    
    return {'suggestions': suggestions}