#!/usr/bin/env python3
"""
Test script to manually trigger notifications
Run this after starting the notification microservice
"""

import requests
import sys

NOTIFICATION_URL = "http://localhost:5001/api/notifications"

def create_test_notification(user_id, notification_type, title, message):
    """Create a test notification"""
    data = {
        "user_id": user_id,
        "type": notification_type,
        "title": title,
        "message": message,
        "link": f"/posts/{user_id}",
        "actor_id": 999,
        "actor_name": "Test User",
        "actor_avatar": None
    }
    
    try:
        response = requests.post(NOTIFICATION_URL, json=data)
        if response.status_code == 201:
            print(f"✅ Created {notification_type} notification for user {user_id}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_notifications.py <user_id>")
        print("Example: python test_notifications.py 1")
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    
    print(f"\n🔔 Creating test notifications for user {user_id}...\n")
    
    # Test different notification types
    notifications = [
        ("post_like", "New Like", "John Doe liked your post about organic farming"),
        ("comment", "New Comment", "Jane Smith commented: 'Great advice on pest control!'"),
        ("follow", "New Follower", "Mike Johnson started following you"),
        ("community_invite", "Community Invitation", "Sarah invited you to join 'Organic Farmers'"),
        ("expert_response", "Expert Response", "Dr. Green responded to your question about soil health"),
    ]
    
    success_count = 0
    for notif_type, title, message in notifications:
        if create_test_notification(user_id, notif_type, title, message):
            success_count += 1
    
    print(f"\n✨ Created {success_count}/{len(notifications)} test notifications")
    print(f"\n📱 Check your app at http://localhost:5173")
    print(f"   - Look for the notification badge in the header")
    print(f"   - Click the bell icon to see notifications")
    print(f"   - Visit /notifications page for full list\n")

if __name__ == "__main__":
    main()
