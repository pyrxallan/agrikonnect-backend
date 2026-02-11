from flask import Flask, send_from_directory, render_template
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
    # Explicitly allow the frontend origin for API routes and enable credentials/support for preflight
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:3000", "http://localhost:5000"]}}, supports_credentials=True)
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

    # Register routes
    register_routes(api)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app