# Agrikonnect Notification Microservice

A standalone Flask microservice for managing real-time notifications in the Agrikonnect platform.

## Features

- Create and manage notifications
- Real-time unread count tracking
- Notification types: post_like, comment, follow, community_invite, expert_response
- Pagination support
- Mark as read functionality
- Auto-cleanup of old notifications

## API Endpoints

### Health Check
```
GET /health
```

### Create Notification
```
POST /api/notifications
Body: {
  "user_id": 1,
  "type": "post_like",
  "title": "New Like",
  "message": "John liked your post",
  "link": "/posts/123",
  "actor_id": 2,
  "actor_name": "John Doe",
  "actor_avatar": "https://..."
}
```

### Get User Notifications
```
GET /api/notifications/{user_id}?page=1&per_page=20&unread_only=false
```

### Get Unread Count
```
GET /api/notifications/{user_id}/unread-count
```

### Mark as Read
```
PUT /api/notifications/{notification_id}/read
```

### Mark All as Read
```
PUT /api/notifications/{user_id}/read-all
```

### Delete Notification
```
DELETE /api/notifications/{notification_id}
```

### Clear Old Notifications
```
DELETE /api/notifications/{user_id}/clear-old
```

## Running Locally

### With Docker
```bash
docker-compose up -d
```

### Without Docker
```bash
pip install -r requirements.txt
cd app
python app.py
```

Service runs on port 5001.

## Environment Variables

- `DATABASE_URL`: Database connection string (default: sqlite:///notifications.db)

## Integration with Main Backend

Use the `NotificationService` helper class in the main backend:

```python
from app.services import NotificationService

# Send notification
NotificationService.notify_post_like(
    post_author_id=1,
    liker_id=2,
    liker_name="John Doe",
    post_id=123
)
```
