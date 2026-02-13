from flask import Flask, send_from_directory, render_template, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException
import os

from .config import Config
from .extensions import db, mail
from .routes import register_routes
from app.routes.messages import messages_bp
from app.routes.users import users_bp
from app.models import Notification
from app.utils.logging_config import setup_logging, log_request

jwt_blocklist = set()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Setup logging first
    logger = setup_logging(app)
    log_request(app)
    
    logger.info('Initializing Flask extensions...')

    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["1000 per day", "200 per hour"],
        storage_uri="memory://"
    )
    
    # Store limiter in app for route access
    app.limiter = limiter
    
    app.logger.info('Rate limiter initialized')

    CORS(app, 
         resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', ['*'])}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    
    app.logger.info(f'CORS configured for origins: {app.config["CORS_ORIGINS"]}')
    jwt = JWTManager(app)
    db.init_app(app)
    mail.init_app(app)
    Migrate(app, db)
    
    app.logger.info('Database and authentication initialized')

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload['jti'] in jwt_blocklist
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': 'Access denied'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return {'error': 'File too large', 'message': 'Request exceeds maximum size limit'}, 413
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return {'error': 'Too many requests', 'message': 'Rate limit exceeded. Please try again later'}, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}', exc_info=True)
        return {'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        if isinstance(error, HTTPException):
            return {'error': error.name, 'message': error.description}, error.code
        db.session.rollback()
        app.logger.error(f'Unhandled Exception: {error}', exc_info=True)
        return {'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500

    api = Api(app, title='Agrikonnect API', version='1.0', doc=False)

    @app.route('/api/docs')
    def swagger_ui():
        return render_template('swagger.html')

    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory('app/static', filename)

    @app.route('/uploads/<path:filename>')
    def uploaded_files(filename):
        return send_from_directory(os.path.join(app.root_path, '..', 'uploads'), filename)

    register_routes(api)
    app.register_blueprint(messages_bp, url_prefix='/api/v1')
    app.register_blueprint(users_bp, url_prefix='/api/v1')
    
    app.logger.info('Routes registered successfully')


    with app.app_context():
        db.create_all()
        app.logger.info('Database tables created/verified')
    
    app.logger.info('Application initialization complete')
    return app