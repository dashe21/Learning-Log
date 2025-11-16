"""
Topic and entry management routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from models import Topic, Entry, Tag, db
from forms import TopicForm, EntryForm

topics_bp = Blueprint('topics', __name__)

@topics_bp.route('/')
@login_required
def index():
    """List all topics for current user"""
    page = request.args.get('page', 1, type=int)
    topics = Topic.query.filter_by(user_id=current_user.id).order_by(Topic.date_created.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('topics/index.html', topics=topics)

@topics_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new topic"""
    form = TopicForm()
    if form.validate_on_submit():
        topic = Topic(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(topic)
        
        # Process tags
        if form.tags.data:
            tag_names = [name.strip() for name in form.tags.data.split(',') if name.strip()]
            topic_tags = []
            for tag_name in tag_names:
                # Get or create tag
                tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=current_user.id)
                    db.session.add(tag)
                topic_tags.append(tag)
            topic.tags = topic_tags
        
        db.session.commit()
        flash(f'Topic "{topic.name}" created successfully!', 'success')
        return redirect(url_for('topics.view', id=topic.id))
    
    return render_template('topics/create.html', form=form)

@topics_bp.route('/<int:id>')
@login_required
def view(id):
    """View a specific topic and its entries"""
    topic = Topic.query.get_or_404(id)
    if topic.user_id != current_user.id:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    entries = Entry.query.filter_by(topic_id=topic.id).order_by(Entry.date_created.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    
    # Get related topics by tags
    related_topics = []
    if topic.tags:
        tag_ids = [tag.id for tag in topic.tags]
        related_topics = Topic.query.filter(
            Topic.user_id == current_user.id,
            Topic.id != topic.id,
            Topic.tags.any(Tag.id.in_(tag_ids))
        ).limit(5).all()
    
    return render_template('topics/view.html', topic=topic, entries=entries, related_topics=related_topics)

@topics_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a topic"""
    topic = Topic.query.get_or_404(id)
    if topic.user_id != current_user.id:
        abort(403)
    
    form = TopicForm(obj=topic)
    if form.validate_on_submit():
        topic.name = form.name.data
        topic.description = form.description.data
        
        # Process tags
        topic.tags.clear()  # Remove existing tags
        if form.tags.data:
            tag_names = [name.strip() for name in form.tags.data.split(',') if name.strip()]
            topic_tags = []
            for tag_name in tag_names:
                # Get or create tag
                tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=current_user.id)
                    db.session.add(tag)
                topic_tags.append(tag)
            topic.tags = topic_tags
        
        db.session.commit()
        flash(f'Topic "{topic.name}" updated successfully!', 'success')
        return redirect(url_for('topics.view', id=topic.id))
    
    return render_template('topics/edit.html', form=form, topic=topic)

@topics_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a topic"""
    topic = Topic.query.get_or_404(id)
    if topic.user_id != current_user.id:
        abort(403)
    
    topic_name = topic.name
    db.session.delete(topic)
    db.session.commit()
    flash(f'Topic "{topic_name}" deleted successfully!', 'success')
    return redirect(url_for('topics.index'))

@topics_bp.route('/<int:topic_id>/entries/create', methods=['GET', 'POST'])
@login_required
def create_entry(topic_id):
    """Create a new entry for a topic"""
    topic = Topic.query.get_or_404(topic_id)
    if topic.user_id != current_user.id:
        abort(403)
    
    form = EntryForm()
    # Pre-populate with topic tags
    if not form.tags.data and topic.tags:
        form.tags.data = ','.join([tag.name for tag in topic.tags])
    
    if form.validate_on_submit():
        entry = Entry(
            title=form.title.data,
            content=form.content.data,
            topic_id=topic.id
        )
        db.session.add(entry)
        
        # Process tags
        if form.tags.data:
            tag_names = [name.strip() for name in form.tags.data.split(',') if name.strip()]
            entry_tags = []
            for tag_name in tag_names:
                # Get or create tag
                tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=current_user.id)
                    db.session.add(tag)
                entry_tags.append(tag)
            entry.tags = entry_tags
        
        db.session.commit()
        flash(f'Entry "{entry.title}" added successfully!', 'success')
        return redirect(url_for('topics.view', id=topic.id))
    
    return render_template('topics/create_entry.html', form=form, topic=topic)

@topics_bp.route('/<int:topic_id>/entries/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(topic_id, entry_id):
    """Edit an entry"""
    topic = Topic.query.get_or_404(topic_id)
    entry = Entry.query.get_or_404(entry_id)
    
    if topic.user_id != current_user.id or entry.topic_id != topic.id:
        abort(403)
    
    form = EntryForm(obj=entry)
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.content = form.content.data
        
        # Process tags
        entry.tags.clear()  # Remove existing tags
        if form.tags.data:
            tag_names = [name.strip() for name in form.tags.data.split(',') if name.strip()]
            entry_tags = []
            for tag_name in tag_names:
                # Get or create tag
                tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=current_user.id)
                    db.session.add(tag)
                entry_tags.append(tag)
            entry.tags = entry_tags
        
        db.session.commit()
        flash(f'Entry "{entry.title}" updated successfully!', 'success')
        return redirect(url_for('topics.view', id=topic.id))
    
    return render_template('topics/edit_entry.html', form=form, topic=topic, entry=entry)

@topics_bp.route('/<int:topic_id>/entries/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(topic_id, entry_id):
    """Delete an entry"""
    topic = Topic.query.get_or_404(topic_id)
    entry = Entry.query.get_or_404(entry_id)
    
    if topic.user_id != current_user.id or entry.topic_id != topic.id:
        abort(403)
    
    entry_title = entry.title
    db.session.delete(entry)
    db.session.commit()
    flash(f'Entry "{entry_title}" deleted successfully!', 'success')
    return redirect(url_for('topics.view', id=topic.id))