from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config
from .extensions import db, mail
# Register routes
from .routes import register_routes
from app.routes.messages import messages_bp
# JWT token blocklist for logout functionality
jwt_blocklist = set()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    
    @limiter.limit("5 per minute")
    def login():
        pass

    # Initialize extensions
    # CORS configuration - allow frontend origins with credentials
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    jwt = JWTManager(app)
    db.init_app(app)
    mail.init_app(app)
    Migrate(app, db)

    # JWT blocklist callback
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in jwt_blocklist

    # Swagger API
    api = Api(
        app,
        title='Agrikonnect API',
        version='1.0',
        description='RESTful API for Agrikonnect agricultural platform. This API provides endpoints for user authentication, community management, expert consultations, and agricultural content sharing.',
        doc=False
    )

    # Custom Swagger UI route
    @app.route('/api/docs')
    def swagger_ui():
        return render_template('swagger.html')

    # Serve static files
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory('app/static', filename)

    # Register other routes
    register_routes(api)
    # Register legacy blueprint for clients calling /messages/*
    app.register_blueprint(messages_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
