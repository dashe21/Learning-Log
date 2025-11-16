"""
Analytics and statistics for Learning Log application
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import Topic, Entry, db
from sqlalchemy import func, extract
from datetime import datetime, timedelta, timezone
import calendar

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def dashboard():
    """Analytics dashboard with learning statistics"""
    
    # Basic counts
    total_topics = Topic.query.filter_by(user_id=current_user.id).count()
    total_entries = Entry.query.join(Topic).filter(Topic.user_id == current_user.id).count()
    
    # Calculate learning streak
    learning_streak = calculate_learning_streak()
    
    # Most active topic
    most_active_topic = get_most_active_topic()
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_entries = Entry.query.join(Topic).filter(
        Topic.user_id == current_user.id,
        Entry.date_created >= thirty_days_ago
    ).count()
    
    # Weekly activity for chart
    weekly_data = get_weekly_activity()
    
    # Monthly entry counts
    monthly_data = get_monthly_entry_counts()
    
    # Word count statistics
    word_stats = get_word_count_stats()
    
    return render_template('analytics/dashboard.html',
                         total_topics=total_topics,
                         total_entries=total_entries,
                         learning_streak=learning_streak,
                         most_active_topic=most_active_topic,
                         recent_entries=recent_entries,
                         weekly_data=weekly_data,
                         monthly_data=monthly_data,
                         word_stats=word_stats)

@analytics_bp.route('/analytics/api/chart-data')
@login_required
def chart_data():
    """API endpoint for chart data"""
    chart_type = request.args.get('type', 'monthly')
    
    if chart_type == 'monthly':
        data = get_monthly_entry_counts()
    elif chart_type == 'weekly':
        data = get_weekly_activity()
    elif chart_type == 'topics':
        data = get_topic_entry_counts()
    else:
        data = []
    
    return jsonify(data)

def calculate_learning_streak():
    """Calculate current learning streak in days"""
    entries = Entry.query.join(Topic).filter(
        Topic.user_id == current_user.id
    ).order_by(Entry.date_created.desc()).all()
    
    if not entries:
        return 0
    
    # Get unique dates of entries
    entry_dates = set()
    for entry in entries:
        entry_date = entry.date_created.date()
        entry_dates.add(entry_date)
    
    # Sort dates in descending order
    sorted_dates = sorted(entry_dates, reverse=True)
    
    if not sorted_dates:
        return 0
    
    # Check if today or yesterday has entries
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    
    streak = 0
    current_date = today
    
    # Start from today or yesterday if there are entries
    if today in sorted_dates:
        streak = 1
        current_date = yesterday
    elif yesterday in sorted_dates:
        streak = 1
        current_date = yesterday - timedelta(days=1)
    else:
        return 0
    
    # Count consecutive days
    for date in sorted_dates:
        if date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        elif date < current_date:
            break
    
    return streak

def get_most_active_topic():
    """Get topic with most entries"""
    result = db.session.query(
        Topic.name,
        func.count(Entry.id).label('entry_count')
    ).join(Entry).filter(
        Topic.user_id == current_user.id
    ).group_by(Topic.id).order_by(
        func.count(Entry.id).desc()
    ).first()
    
    if result:
        return {'name': result.name, 'count': result.entry_count}
    return None

def get_weekly_activity():
    """Get activity for the last 7 days"""
    weekly_data = []
    
    for i in range(6, -1, -1):
        date = datetime.now(timezone.utc).date() - timedelta(days=i)
        
        count = Entry.query.join(Topic).filter(
            Topic.user_id == current_user.id,
            func.date(Entry.date_created) == date
        ).count()
        
        weekly_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%a'),
            'count': count
        })
    
    return weekly_data

def get_monthly_entry_counts():
    """Get entry counts by month for the last 12 months"""
    monthly_data = []
    
    for i in range(11, -1, -1):
        # Calculate the target month
        target_date = datetime.now(timezone.utc) - timedelta(days=i*30)
        year = target_date.year
        month = target_date.month
        
        count = Entry.query.join(Topic).filter(
            Topic.user_id == current_user.id,
            extract('year', Entry.date_created) == year,
            extract('month', Entry.date_created) == month
        ).count()
        
        monthly_data.append({
            'month': f"{calendar.month_abbr[month]} {year}",
            'count': count,
            'year': year,
            'month_num': month
        })
    
    return monthly_data[-6:]  # Return last 6 months

def get_topic_entry_counts():
    """Get entry counts by topic"""
    results = db.session.query(
        Topic.name,
        func.count(Entry.id).label('count')
    ).join(Entry).filter(
        Topic.user_id == current_user.id
    ).group_by(Topic.id).order_by(
        func.count(Entry.id).desc()
    ).limit(10).all()
    
    return [{'topic': result.name, 'count': result.count} for result in results]

def get_word_count_stats():
    """Calculate word count statistics"""
    entries = Entry.query.join(Topic).filter(
        Topic.user_id == current_user.id
    ).all()
    
    if not entries:
        return {'total': 0, 'average': 0, 'longest': 0}
    
    word_counts = []
    for entry in entries:
        word_count = len(entry.content.split())
        word_counts.append(word_count)
    
    total_words = sum(word_counts)
    average_words = round(total_words / len(word_counts))
    longest_entry = max(word_counts)
    
    return {
        'total': total_words,
        'average': average_words,
        'longest': longest_entry,
        'entries': len(entries)
    }