"""
Logging configuration for Agrikonnect
"""
import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime

def setup_logging(app):
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set logging level based on environment
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
    
    # Remove default handlers
    app.logger.handlers.clear()
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    app.logger.addHandler(console_handler)
    
    # File handler for all logs (rotating by size)
    file_handler = RotatingFileHandler(
        'logs/agrikonnect.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)
    
    # Error file handler (rotating daily)
    error_handler = TimedRotatingFileHandler(
        'logs/errors.log',
        when='midnight',
        interval=1,
        backupCount=30
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    app.logger.addHandler(error_handler)
    
    # Access log handler (rotating daily)
    access_handler = TimedRotatingFileHandler(
        'logs/access.log',
        when='midnight',
        interval=1,
        backupCount=30
    )
    access_handler.setLevel(logging.INFO)
    access_formatter = logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    access_handler.setFormatter(access_formatter)
    
    # Create access logger
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    
    # Log startup
    app.logger.info('='*50)
    app.logger.info('Agrikonnect Application Starting')
    app.logger.info(f'Environment: {"Development" if app.debug else "Production"}')
    app.logger.info(f'Database: {app.config.get("SQLALCHEMY_DATABASE_URI", "").split("@")[-1] if "@" in app.config.get("SQLALCHEMY_DATABASE_URI", "") else "SQLite"}')
    app.logger.info('='*50)
    
    return app.logger

def log_request(app):
    """Log HTTP requests"""
    @app.before_request
    def before_request():
        from flask import request
        access_logger = logging.getLogger('access')
        access_logger.info(f'{request.remote_addr} - {request.method} {request.path}')
    
    @app.after_request
    def after_request(response):
        from flask import request
        access_logger = logging.getLogger('access')
        access_logger.info(
            f'{request.remote_addr} - {request.method} {request.path} - '
            f'{response.status_code} - {response.content_length or 0} bytes'
        )
        return response
