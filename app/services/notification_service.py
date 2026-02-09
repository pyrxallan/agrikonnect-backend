import requests
import os
from typing import Optional

NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:5001')

class NotificationService:
    @staticmethod
    def send_notification(
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        link: Optional[str] = None,
        actor_id: Optional[int] = None,
        actor_name: Optional[str] = None,
        actor_avatar: Optional[str] = None
    ):
        """Send notification to notification microservice"""
        try:
            response = requests.post(
                f'{NOTIFICATION_SERVICE_URL}/api/notifications',
                json={
                    'user_id': user_id,
                    'type': notification_type,
                    'title': title,
                    'message': message,
                    'link': link,
                    'actor_id': actor_id,
                    'actor_name': actor_name,
                    'actor_avatar': actor_avatar
                },
                timeout=5
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False
    
    @staticmethod
    def notify_post_like(post_author_id: int, liker_id: int, liker_name: str, post_id: int):
        """Notify when someone likes a post"""
        return NotificationService.send_notification(
            user_id=post_author_id,
            notification_type='post_like',
            title='New Like',
            message=f'{liker_name} liked your post',
            link=f'/posts/{post_id}',
            actor_id=liker_id,
            actor_name=liker_name
        )
    
    @staticmethod
    def notify_comment(post_author_id: int, commenter_id: int, commenter_name: str, post_id: int):
        """Notify when someone comments on a post"""
        return NotificationService.send_notification(
            user_id=post_author_id,
            notification_type='comment',
            title='New Comment',
            message=f'{commenter_name} commented on your post',
            link=f'/posts/{post_id}',
            actor_id=commenter_id,
            actor_name=commenter_name
        )
    
    @staticmethod
    def notify_follow(followed_id: int, follower_id: int, follower_name: str):
        """Notify when someone follows an expert"""
        return NotificationService.send_notification(
            user_id=followed_id,
            notification_type='follow',
            title='New Follower',
            message=f'{follower_name} started following you',
            link=f'/experts/{follower_id}',
            actor_id=follower_id,
            actor_name=follower_name
        )
    
    @staticmethod
    def notify_community_invite(user_id: int, community_id: int, community_name: str, inviter_name: str):
        """Notify when invited to a community"""
        return NotificationService.send_notification(
            user_id=user_id,
            notification_type='community_invite',
            title='Community Invitation',
            message=f'{inviter_name} invited you to join {community_name}',
            link=f'/communities/{community_id}'
        )
    
    @staticmethod
    def notify_expert_response(user_id: int, expert_id: int, expert_name: str, post_id: int):
        """Notify when an expert responds to a question"""
        return NotificationService.send_notification(
            user_id=user_id,
            notification_type='expert_response',
            title='Expert Response',
            message=f'{expert_name} responded to your question',
            link=f'/posts/{post_id}',
            actor_id=expert_id,
            actor_name=expert_name
        )
    
    @staticmethod
    def notify_community_post(community_id: int, member_ids: list, author_name: str, post_id: int):
        """Notify community members of new post"""
        for member_id in member_ids:
            NotificationService.send_notification(
                user_id=member_id,
                notification_type='community_post',
                title='New Community Post',
                message=f'{author_name} posted in your community',
                link=f'/posts/{post_id}'
            )
