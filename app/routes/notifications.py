from flask_restx import Namespace, Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os

notification_ns = Namespace('notifications', description='Notification operations')

NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:5001')

@notification_ns.route('')
class NotificationList(Resource):
    @jwt_required()
    def get(self):
        """Get notifications for current user"""
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false')
        
        try:
            response = requests.get(
                f'{NOTIFICATION_SERVICE_URL}/api/notifications/{user_id}',
                params={'page': page, 'per_page': per_page, 'unread_only': unread_only},
                timeout=5
            )
            return response.json(), response.status_code
        except:
            return {'notifications': [], 'total': 0, 'unread_count': 0}, 200

@notification_ns.route('/<int:notification_id>/read')
class NotificationRead(Resource):
    @jwt_required()
    def put(self, notification_id):
        """Mark notification as read"""
        try:
            response = requests.put(
                f'{NOTIFICATION_SERVICE_URL}/api/notifications/{notification_id}/read',
                timeout=5
            )
            return response.json(), response.status_code
        except:
            return {'message': 'Failed to mark as read'}, 500

@notification_ns.route('/read-all')
class NotificationReadAll(Resource):
    @jwt_required()
    def put(self):
        """Mark all notifications as read"""
        user_id = get_jwt_identity()
        try:
            response = requests.put(
                f'{NOTIFICATION_SERVICE_URL}/api/notifications/{user_id}/read-all',
                timeout=5
            )
            return response.json(), response.status_code
        except:
            return {'message': 'Failed to mark all as read'}, 500

@notification_ns.route('/unread-count')
class NotificationUnreadCount(Resource):
    @jwt_required()
    def get(self):
        """Get unread notification count"""
        user_id = get_jwt_identity()
        try:
            response = requests.get(
                f'{NOTIFICATION_SERVICE_URL}/api/notifications/{user_id}/unread-count',
                timeout=5
            )
            return response.json(), response.status_code
        except:
            return {'count': 0}, 200

@notification_ns.route('/<int:notification_id>')
class NotificationDelete(Resource):
    @jwt_required()
    def delete(self, notification_id):
        """Delete a notification"""
        try:
            response = requests.delete(
                f'{NOTIFICATION_SERVICE_URL}/api/notifications/{notification_id}',
                timeout=5
            )
            return response.json(), response.status_code
        except:
            return {'message': 'Failed to delete'}, 500
