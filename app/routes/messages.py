from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource
from app.models.message import Message
from app.models.user import User
from app.extensions import db

message_ns = Namespace('messages', description='User messages')


@message_ns.route('/')
class SendMessage(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        receiver_id = data.get('receiver_id')
        content = data.get('content')

        if not receiver_id or not content:
            return {'error': 'receiver_id and content required'}, 400

        if receiver_id == user_id:
            return {'error': 'Cannot send message to yourself'}, 400

        receiver = User.query.get(receiver_id)
        if not receiver:
            return {'error': 'Receiver not found'}, 404

        message = Message(sender_id=user_id, receiver_id=receiver_id, content=content)
        db.session.add(message)
        db.session.commit()

        return message.to_dict(), 201


@message_ns.route('/inbox')
class Inbox(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        messages = Message.query.filter_by(receiver_id=user_id).order_by(Message.created_at.desc()).all()
        return [m.to_dict() for m in messages], 200


@message_ns.route('/sent')
class SentMessages(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        messages = Message.query.filter_by(sender_id=user_id).order_by(Message.created_at.desc()).all()
        return [m.to_dict() for m in messages], 200


@message_ns.route('/<int:message_id>/read')
class MarkAsRead(Resource):
    @jwt_required()
    def patch(self, message_id):
        user_id = get_jwt_identity()
        message = Message.query.get_or_404(message_id)

        if message.receiver_id != user_id:
            return {'error': 'Forbidden'}, 403

        message.mark_as_read()
        db.session.commit()
        return message.to_dict(), 200
