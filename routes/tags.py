"""
Tag and Category management routes for Learning Log application
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from models import db, Tag, Category, Topic, Entry
from forms import TagForm, CategoryForm
from sqlalchemy import func, or_

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/tags')
@login_required
def index():
    """List all tags and categories for current user"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category_filter = request.args.get('category', '', type=str)
    sort_by = request.args.get('sort', 'name', type=str)
    
    # Base query for user's tags
    query = Tag.query.filter_by(user_id=current_user.id)
    
    # Apply search filter
    if search:
        query = query.filter(or_(
            Tag.name.contains(search),
            Tag.description.contains(search)
        ))
    
    # Apply category filter
    if category_filter:
        if category_filter == 'uncategorized':
            query = query.filter(Tag.category_id.is_(None))
        else:
            try:
                cat_id = int(category_filter)
                query = query.filter(Tag.category_id == cat_id)
            except ValueError:
                pass
    
    # Apply sorting
    if sort_by == 'usage':
        # Sort by usage count (topics + entries)
        query = query.outerjoin(Tag.topics).outerjoin(Tag.entries).group_by(Tag.id).order_by(
            func.count(Tag.topics) + func.count(Tag.entries).desc(), Tag.name
        )
    elif sort_by == 'created':
        query = query.order_by(Tag.date_created.desc())
    else:  # name
        query = query.order_by(Tag.name)
    
    # Paginate results
    tags = query.paginate(page=page, per_page=20, error_out=False)
    
    # Get categories for filter dropdown
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    
    # Get tag usage statistics
    total_tags = Tag.query.filter_by(user_id=current_user.id).count()
    total_categories = Category.query.filter_by(user_id=current_user.id).count()
    
    return render_template('tags/index.html',
                         tags=tags,
                         categories=categories,
                         search=search,
                         category_filter=category_filter,
                         sort_by=sort_by,
                         total_tags=total_tags,
                         total_categories=total_categories)

@tags_bp.route('/tags/create', methods=['GET', 'POST'])
@login_required
def create_tag():
    """Create a new tag"""
    form = TagForm()
    
    if form.validate_on_submit():
        tag = Tag(
            name=form.name.data.strip(),
            description=form.description.data,
            user_id=current_user.id,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            color=form.color.data if form.color.data else None
        )
        db.session.add(tag)
        db.session.commit()
        flash(f'Tag "{tag.name}" created successfully!', 'success')
        return redirect(url_for('tags.index'))
    
    return render_template('tags/create_tag.html', form=form)

@tags_bp.route('/tags/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(id):
    """Edit a tag"""
    tag = Tag.query.get_or_404(id)
    if tag.user_id != current_user.id:
        abort(403)
    
    form = TagForm(obj=tag)
    form.tag_id = tag.id  # For validation
    
    if form.validate_on_submit():
        tag.name = form.name.data.strip()
        tag.description = form.description.data
        tag.category_id = form.category_id.data if form.category_id.data != 0 else None
        tag.color = form.color.data if form.color.data else None
        db.session.commit()
        flash(f'Tag "{tag.name}" updated successfully!', 'success')
        return redirect(url_for('tags.index'))
    
    return render_template('tags/edit_tag.html', form=form, tag=tag)

@tags_bp.route('/tags/<int:id>/delete', methods=['POST'])
@login_required
def delete_tag(id):
    """Delete a tag"""
    tag = Tag.query.get_or_404(id)
    if tag.user_id != current_user.id:
        abort(403)
    
    if not tag.can_delete():
        flash(f'Cannot delete tag "{tag.name}" - it is still being used by {tag.usage_count} items.', 'danger')
        return redirect(url_for('tags.index'))
    
    tag_name = tag.name
    db.session.delete(tag)
    db.session.commit()
    flash(f'Tag "{tag_name}" deleted successfully!', 'success')
    return redirect(url_for('tags.index'))

@tags_bp.route('/categories')
@login_required
def categories():
    """List all categories for current user"""
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    return render_template('tags/categories.html', categories=categories)

@tags_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create a new category"""
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data.strip(),
            description=form.description.data,
            color=form.color.data,
            icon=form.icon.data,
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{category.name}" created successfully!', 'success')
        return redirect(url_for('tags.categories'))
    
    return render_template('tags/create_category.html', form=form)

@tags_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """Edit a category"""
    category = Category.query.get_or_404(id)
    if category.user_id != current_user.id:
        abort(403)
    
    form = CategoryForm(obj=category)
    form.category_id = category.id  # For validation
    
    if form.validate_on_submit():
        category.name = form.name.data.strip()
        category.description = form.description.data
        category.color = form.color.data
        category.icon = form.icon.data
        db.session.commit()
        flash(f'Category "{category.name}" updated successfully!', 'success')
        return redirect(url_for('tags.categories'))
    
    return render_template('tags/edit_category.html', form=form, category=category)

@tags_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    """Delete a category"""
    category = Category.query.get_or_404(id)
    if category.user_id != current_user.id:
        abort(403)
    
    if category.tag_count > 0:
        flash(f'Cannot delete category "{category.name}" - it contains {category.tag_count} tags. Please move or delete the tags first.', 'danger')
        return redirect(url_for('tags.categories'))
    
    category_name = category.name
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category_name}" deleted successfully!', 'success')
    return redirect(url_for('tags.categories'))

@tags_bp.route('/api/tags/search')
@login_required
def search_tags():
    """API endpoint for tag autocomplete"""
    query = request.args.get('q', '', type=str)
    limit = request.args.get('limit', 10, type=int)
    
    if len(query) < 1:
        return jsonify([])
    
    tags = Tag.query.filter(
        Tag.user_id == current_user.id,
        Tag.name.contains(query)
    ).limit(limit).all()
    
    return jsonify([{
        'id': tag.id,
        'name': tag.name,
        'color': tag.display_color,
        'category': tag.category.name if tag.category else None,
        'usage_count': tag.usage_count
    } for tag in tags])

@tags_bp.route('/api/tags/suggest')
@login_required 
def suggest_tags():
    """API endpoint for intelligent tag suggestions based on content"""
    content = request.args.get('content', '', type=str)
    topic_id = request.args.get('topic_id', type=int)
    limit = request.args.get('limit', 5, type=int)
    
    suggestions = []
    
    # Get existing tags that match keywords in content
    if content and len(content) > 10:
        words = [word.lower().strip('.,!?;:"()[]{}') 
                for word in content.split() 
                if len(word) > 3]
        
        if words:
            # Find tags that match content words
            matching_tags = Tag.query.filter(
                Tag.user_id == current_user.id,
                or_(*[Tag.name.ilike(f'%{word}%') for word in words[:10]])
            ).limit(limit).all()
            
            suggestions.extend([{
                'name': tag.name,
                'reason': 'Content match',
                'color': tag.display_color
            } for tag in matching_tags])
    
    # If we have a topic, suggest tags used in similar topics
    if topic_id and len(suggestions) < limit:
        from models import Topic
        topic = Topic.query.get(topic_id)
        if topic and topic.user_id == current_user.id:
            # Find tags used in other topics by this user
            similar_tags = Tag.query.join(Tag.topics).filter(
                Tag.user_id == current_user.id,
                Tag.id.notin_([tag.id for tag in topic.tags])
            ).group_by(Tag.id).order_by(func.count(Tag.topics).desc()).limit(limit - len(suggestions)).all()
            
            suggestions.extend([{
                'name': tag.name,
                'reason': 'Used in similar topics',
                'color': tag.display_color
            } for tag in similar_tags])
    
    return jsonify(suggestions[:limit])

@tags_bp.route('/tag/<tag_name>')
@login_required
def view_tag_content(tag_name):
    """View all topics and entries for a specific tag"""
    # Find the tag for current user
    tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
    if not tag:
        flash(f'Tag "{tag_name}" not found.', 'warning')
        return redirect(url_for('tags.index'))
    
    # Get topics with this tag
    topics = Topic.query.filter(
        Topic.user_id == current_user.id,
        Topic.tags.contains(tag)
    ).order_by(Topic.date_created.desc()).all()
    
    # Get entries with this tag
    entries = Entry.query.join(Topic).filter(
        Topic.user_id == current_user.id,
        Entry.tags.contains(tag)
    ).order_by(Entry.date_created.desc()).all()
    
    return render_template('tags/view_tag.html', 
                         tag=tag, 
                         topics=topics, 
                         entries=entries)