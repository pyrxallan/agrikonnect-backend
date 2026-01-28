from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api

from .config import Config
from .extensions import db
from .routes import register_routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    JWTManager(app)
    db.init_app(app)
    Migrate(app, db)

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