from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.message import Message
from app.models.user import User
from app.extensions import db

messages_bp = Blueprint("messages", __name__, url_prefix="/messages")

# Send a message
@messages_bp.route("/", methods=["POST"])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()
    data = request.get_json()

    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not receiver_id or not content:
        return jsonify({"error": "receiver_id and content required"}), 400

    if receiver_id == user_id:
        return jsonify({"error": "Cannot send message to yourself"}), 400

    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({"error": "Receiver not found"}), 404

    message = Message(sender_id=user_id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict()), 201

# Inbox
@messages_bp.route("/inbox", methods=["GET"])
@jwt_required()
def inbox():
    user_id = get_jwt_identity()
    messages = Message.query.filter_by(receiver_id=user_id).order_by(Message.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages]), 200

# Sent messages
@messages_bp.route("/sent", methods=["GET"])
@jwt_required()
def sent_messages():
    user_id = get_jwt_identity()
    messages = Message.query.filter_by(sender_id=user_id).order_by(Message.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages]), 200

# Mark message as read
@messages_bp.route("/<int:message_id>/read", methods=["PATCH"])
@jwt_required()
def mark_as_read(message_id):
    user_id = get_jwt_identity()
    message = Message.query.get_or_404(message_id)

    if message.receiver_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    message.mark_as_read()
    db.session.commit()
    return jsonify(message.to_dict()), 200
