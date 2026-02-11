from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from .config import Config
from .extensions import db, mail
from .routes import register_routes
from app.routes.messages import messages_bp

jwt_blocklist = set()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    CORS(app, 
         origins=["http://localhost:5173", "http://localhost:5174", "*"], 
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    jwt = JWTManager(app)
    db.init_app(app)
    mail.init_app(app)
    Migrate(app, db)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload['jti'] in jwt_blocklist

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
    app.register_blueprint(messages_bp)

    with app.app_context():
        db.create_all()

    return app