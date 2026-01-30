from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api

from .config import Config
from .extensions import db, mail
from .routes import register_routes

# JWT token blocklist for logout functionality
jwt_blocklist = set()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
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
        description='RESTful API for Agrikonnect agricultural platform',
        doc='/api/docs'
    )

    # Register routes
    register_routes(api)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app