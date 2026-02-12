from flask import Flask, send_from_directory, render_template, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import JWTExtendedException, NoAuthorizationError, RevokedTokenError
from jwt import ExpiredSignatureError
from flask_migrate import Migrate
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from .config import Config
from .extensions import db, mail
from .routes import register_routes
from app.routes.messages import messages_bp
from app.routes.users import users_bp

jwt_blocklist = set()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["1000 per day", "200 per hour"],
        storage_uri="memory://"
    )

    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    jwt = JWTManager(app)
    db.init_app(app)
    mail.init_app(app)
    Migrate(app, db)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload['jti'] in jwt_blocklist

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify(message="Token has expired"), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(message="Invalid token"), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify(message="Missing token"), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify(message="Token has been revoked"), 401

    api = Api(app, title='Agrikonnect API', version='1.0', doc=False)

    @api.errorhandler(ExpiredSignatureError)
    def handle_expired_signature_error(error):
        return {'message': 'Token has expired'}, 401

    @api.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(error):
        return {'message': 'Missing token'}, 401

    @api.errorhandler(RevokedTokenError)
    def handle_revoked_token_error(error):
        return {'message': 'Token has been revoked'}, 401

    @api.errorhandler(JWTExtendedException)
    def handle_jwt_extended_error(error):
        return {'message': 'Invalid token'}, 401

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
    app.register_blueprint(users_bp)


    with app.app_context():
        db.create_all()

    return app