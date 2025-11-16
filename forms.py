"""
Forms for Learning Log application using Flask-WTF
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from wtforms.widgets import ColorInput
from flask_login import current_user

class ColorField(StringField):
    """Custom color picker field"""
    widget = ColorInput()

class TagSelectionField(StringField):
    """Custom field for tag selection with autocomplete"""
    def __init__(self, *args, **kwargs):
        super(TagSelectionField, self).__init__(*args, **kwargs)
        self.render_kw = self.render_kw or {}
        self.render_kw.update({
            'class': 'form-control tag-input',
            'data-role': 'tagsinput',
            'placeholder': 'Type tag names, press Enter to add...'
        })

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Registration form"""
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=20, message='Username must be between 4 and 20 characters')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username is already taken"""
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered"""
        from models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class TopicForm(FlaskForm):
    """Topic creation and editing form"""
    name = StringField('Topic Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Topic name must be between 2 and 100 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=500, message='Description cannot exceed 500 characters')
    ], render_kw={'class': 'rich-text-editor', 'rows': 6})
    tags = TagSelectionField('Tags', render_kw={
        'placeholder': 'Add tags to organize this topic...'
    })
    submit = SubmitField('Save Topic')

class EntryForm(FlaskForm):
    """Entry creation and editing form"""
    title = StringField('Entry Title', validators=[
        DataRequired(),
        Length(min=2, max=200, message='Title must be between 2 and 200 characters')
    ])
    content = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=10, message='Content must be at least 10 characters long')
    ], render_kw={
        'class': 'rich-text-editor', 
        'rows': 12,
        'data-validation': 'false'
    })
    tags = TagSelectionField('Tags', render_kw={
        'placeholder': 'Add tags to categorize this entry...'
    })
    submit = SubmitField('Save Entry')

# Tag and Category Forms
class CategoryForm(FlaskForm):
    """Category creation and editing form"""
    name = StringField('Category Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='Category name must be between 2 and 50 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=200, message='Description cannot exceed 200 characters')
    ], render_kw={'rows': 3})
    color = ColorField('Color', validators=[DataRequired()], default='#6c757d')
    icon = SelectField('Icon', validators=[DataRequired()], choices=[
        ('bi-tag', '🏷️ Tag'),
        ('bi-bookmark', '🔖 Bookmark'), 
        ('bi-star', '⭐ Star'),
        ('bi-heart', '❤️ Heart'),
        ('bi-lightbulb', '💡 Lightbulb'),
        ('bi-book', '📚 Book'),
        ('bi-code-slash', '💻 Code'),
        ('bi-graph-up', '📈 Graph'),
        ('bi-gear', '⚙️ Gear'),
        ('bi-trophy', '🏆 Trophy'),
        ('bi-flag', '🚩 Flag'),
        ('bi-puzzle', '🧩 Puzzle')
    ], default='bi-tag')
    submit = SubmitField('Save Category')
    
    def validate_name(self, name):
        """Check if category name is already taken by current user"""
        from models import Category
        category = Category.query.filter_by(
            name=name.data, 
            user_id=current_user.id
        ).first()
        
        # Allow if editing the same category
        if category and (not hasattr(self, 'category_id') or category.id != getattr(self, 'category_id', None)):
            raise ValidationError('Category name already exists. Please choose a different name.')

class TagForm(FlaskForm):
    """Tag creation and editing form"""
    name = StringField('Tag Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='Tag name must be between 2 and 50 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=200, message='Description cannot exceed 200 characters')
    ], render_kw={'rows': 2})
    category_id = SelectField('Category', validators=[Optional()], coerce=int)
    color = ColorField('Custom Color (optional)', validators=[Optional()], 
                      render_kw={'placeholder': 'Leave empty to use category color'})
    submit = SubmitField('Save Tag')
    
    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        # Populate categories for current user
        from models import Category
        self.category_id.choices = [(0, 'No Category')] + [
            (cat.id, cat.name) for cat in 
            Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
        ]
    
    def validate_name(self, name):
        """Check if tag name is already taken by current user"""
        from models import Tag
        tag = Tag.query.filter_by(
            name=name.data,
            user_id=current_user.id
        ).first()
        
        # Allow if editing the same tag
        if tag and (not hasattr(self, 'tag_id') or tag.id != getattr(self, 'tag_id', None)):
            raise ValidationError('Tag name already exists. Please choose a different name.')