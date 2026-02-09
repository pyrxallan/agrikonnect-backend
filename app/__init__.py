from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config
from .extensions import db, mail
from .routes import register_routes

# JWT token blocklist for logout functionality
jwt_blocklist = set()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize rate limiter with more generous limits for development
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["1000 per day", "200 per hour"],
        storage_uri="memory://"
    )

    # Apply to auth routes
    @limiter.limit("5 per minute")
    def login():
        pass

    # Initialize extensions - Allow all origins for development
    CORS(app, origins="*", supports_credentials=True)
    jwt = JWTManager(app)
    db.init_app(app)
    mail.init_app(app)
    Migrate(app, db)

    # JWT blocklist callback
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in jwt_blocklist

    # Initialize API
    api = Api(
        app,
        title='Agrikonnect API',
        version='1.0',
        description='RESTful API for Agrikonnect agricultural platform. This API provides endpoints for user authentication, community management, expert consultations, and agricultural content sharing.',
        doc='/api/docs',
        contact='Agrikonnect Team',
        contact_email='support@agrikonnect.com',
        license='MIT',
        license_url='https://opensource.org/licenses/MIT'
    )

    # Register routes
    register_routes(api)

    # Serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app