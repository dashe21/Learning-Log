"""
Security enhancements for Flask application
"""
import os
from flask import Flask


def configure_security_headers(app: Flask) -> None:
    """Configure security headers for the Flask application"""
    
    # Check if security headers are enabled
    if os.environ.get('SECURE_HEADERS', 'true').lower() not in ('true', '1', 'yes'):
        return
    
    @app.after_request
    def set_security_headers(response):
        """Set security headers on all responses"""
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tiny.cloud; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        
        # Other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS (only if not disabled via SSL_DISABLE)
        if os.environ.get('SSL_DISABLE', 'false').lower() not in ('true', '1', 'yes'):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


def configure_session_security(app: Flask) -> None:
    """Configure secure session settings"""
    
    # Session cookie security
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SSL_DISABLE', 'false').lower() not in ('true', '1', 'yes')
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Remember me cookie security
    app.config['REMEMBER_COOKIE_SECURE'] = app.config['SESSION_COOKIE_SECURE']
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_DURATION'] = 3600 * 24 * 7  # 7 days


def configure_app_security(app: Flask) -> None:
    """Configure all security settings for the application"""
    configure_security_headers(app)
    configure_session_security(app)
    
    # Additional Flask security settings
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour CSRF token lifetime
    
    return app