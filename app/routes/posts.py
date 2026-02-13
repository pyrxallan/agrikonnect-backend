
from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from ..models import Post, Comment, User
from ..extensions import db
from ..utils.validation import (
    validate_required_fields,
    validate_string_length,
    sanitize_string,
    validate_url
)
# handle file uploads securely
from werkzeug.utils import secure_filename
import os

post_ns = Namespace('posts', description='Post operations')

# Models for API documentation and validation
post_model = post_ns.model('Post', {
    'title': fields.String(required=True, description='Post title', min_length=1, max_length=255),
    'content': fields.String(required=True, description='Post content', min_length=1),
    'image_url': fields.String(description='Image URL', max_length=500),
    'community_id': fields.Integer(description='Community ID')
})

comment_model = post_ns.model('Comment', {
    'content': fields.String(required=True, description='Comment content', min_length=1, max_length=1000)
})

# File upload handling in post creation
@post_ns.route('')
class PostList(Resource):
    @post_ns.doc('list_posts', params={
        'page': 'Page number (default: 1)',
        'per_page': 'Items per page (default: 20, max: 100)',
        'author_id': 'Filter by author ID'
    })
    def get(self):
        """Get paginated list of posts"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            author_id = request.args.get('author_id', type=int)
            
            if page < 1:
                return {'error': 'Page must be >= 1'}, 400
            if per_page < 1:
                return {'error': 'Per page must be >= 1'}, 400
            
            query = Post.query
            if author_id:
                query = query.filter_by(author_id=author_id)
            
            # Load author relationships
            try:
                query = query.options(joinedload(Post.author))
            except AttributeError:
                # If relationship attribute isn't available skip eager loading
                current_app.logger.warning('Post.author relationship not available for joinedload; skipping eager load')
            
            paginated = query.order_by(Post.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # Serialize posts with current user context 
            posts_list = []
            current_user_id = None
            try:
                current_user_id = int(get_jwt_identity())
            except:
                pass
            
            for p in paginated.items:
                try:
                    posts_list.append(p.to_dict(current_user_id=current_user_id))
                except Exception:
                    current_app.logger.exception('Failed to serialize post id=%s', getattr(p, 'id', None))
                    # skip problematic post
                    continue

            return {
                'posts': posts_list,
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            current_app.logger.exception('Failed to fetch posts')
            return {'error': 'Failed to fetch posts'}, 500
    
    # Create post with optional image upload
    @jwt_required()
    @post_ns.doc('create_post', params={})
    def post(self):
        """Create a new post (accepts optional image upload)"""
        try:
            current_user_id = get_jwt_identity()
            
            # Log request details
            current_app.logger.info(f'POST /api/v1/posts - Content-Type: {request.content_type}')
            current_app.logger.info(f'Form data present: {bool(request.form)}')
            current_app.logger.info(f'Files: {list(request.files.keys())}')
            
            # Support both form data and JSON
            if request.form:
                data = request.form.to_dict()
                current_app.logger.info(f'Using form data: {list(data.keys())}')
            else:
                try:
                    data = request.get_json(force=True, silent=False) or {}
                    current_app.logger.info(f'Using JSON data: {list(data.keys())}')
                except Exception as e:
                    current_app.logger.error(f'Failed to parse JSON: {str(e)}')
                    data = {}

            # Validate required fields - only content is required, title can be derived
            is_valid, error = validate_required_fields(data, ['content'])
            if not is_valid:
                current_app.logger.warning(f'Validation failed: {error} - Received fields: {list(data.keys())}')
                return {'error': error}, 400

            # Sanitize and validate title
            # If title is not provided, use first line of content
            title = data.get('title')
            if not title:
                # Use first line of content as title
                content_raw = data.get('content', '')
                title = content_raw.split('\n')[0] if content_raw else ''
                current_app.logger.info(f'Title not provided, using first line of content: {title[:50]}')
            
            title = sanitize_string(title, 255)
            is_valid, error = validate_string_length(title, 1, 255, 'Title')
            if not is_valid:
                return {'error': error}, 400

            # Clean and validate content
            content = sanitize_string(data.get('content'))
            is_valid, error = validate_string_length(content, 1, None, 'Content')
            if not is_valid:
                return {'error': error}, 400

            # Handle image upload or URL
            image_url = data.get('image_url')
            image_file = request.files.get('image') or request.files.get('file')
            current_app.logger.info(f'Image handling - Available files: {list(request.files.keys())}, File found: {image_file is not None}')
            
            if image_file:
                current_app.logger.info(f'Processing image file: {image_file.filename}')
                filename = secure_filename(image_file.filename)
                if '.' in filename:
                    ext = filename.rsplit('.', 1)[1].lower()
                else:
                    ext = ''
                allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'}
                if ext not in allowed:
                    current_app.logger.warning(f'Invalid image extension: {ext}')
                    return {'error': f'Invalid image file type. Allowed: {", ".join(allowed)}'}, 400

                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                save_dir = os.path.abspath(os.path.join(current_app.root_path, '..', upload_folder))
                os.makedirs(save_dir, exist_ok=True)
                unique_name = f"post_{current_user_id}_{int(__import__('time').time())}.{ext}"
                dest = os.path.join(save_dir, unique_name)
                try:
                    image_file.save(dest)
                    current_app.logger.info(f'Image saved successfully: {dest}')
                    image_url = f"/uploads/{unique_name}"
                except Exception as e:
                    current_app.logger.error(f'Failed to save image: {str(e)}')
                    return {'error': f'Failed to save image: {str(e)}'}, 500
            else:
                current_app.logger.info('No image file provided')

            if image_url:
                image_url = sanitize_string(image_url, 500)
                if image_url and not validate_url(image_url) and not image_url.startswith('/uploads'):
                    return {'error': 'Invalid image URL format'}, 400

            # Create post
            post = Post(
                title=title,
                content=content,
                image_url=image_url,
                author_id=int(current_user_id)
            )

            db.session.add(post)
            db.session.commit()
            
            post_dict = post.to_dict()
            current_app.logger.info(f'Post created successfully - ID: {post.id}, Image URL: {image_url}')
            current_app.logger.info(f'Post response includes: title={post_dict.get("title")}, image_url={post_dict.get("image_url")}')

            return {'message': 'Post created', 'post': post_dict}, 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to create post')
            return {'error': 'Failed to create post'}, 500

@post_ns.route('/<int:post_id>')
class PostDetail(Resource):
    @jwt_required()
    @post_ns.doc('get_post')
    def get(self, post_id):
        """Get a specific post"""
        post = Post.query.get(post_id)
        if not post:
            return {'error': 'Post not found'}, 404
        return {'post': post.to_dict()}
    
    @jwt_required()
    @post_ns.expect(post_model)
    @post_ns.doc('update_post')
    def put(self, post_id):
        """Update a post"""
        try:
            current_user_id = int(get_jwt_identity())
            post = Post.query.get(post_id)
            
            if not post:
                return {'error': 'Post not found'}, 404
            
            if post.author_id != current_user_id:
                return {'error': 'Unauthorized'}, 403
            
            data = request.get_json()
            
            # Update title if provided
            if 'title' in data:
                title = sanitize_string(data['title'], 255)
                is_valid, error = validate_string_length(title, 1, 255, 'Title')
                if not is_valid:
                    return {'error': error}, 400
                post.title = title
            
            # Update content if provided
            if 'content' in data:
                content = sanitize_string(data['content'])
                is_valid, error = validate_string_length(content, 1, None, 'Content')
                if not is_valid:
                    return {'error': error}, 400
                post.content = content
            
            # Update image URL if provided
            if 'image_url' in data:
                image_url = sanitize_string(data['image_url'], 500)
                if image_url and not validate_url(image_url):
                    return {'error': 'Invalid image URL format'}, 400
                post.image_url = image_url
            
            db.session.commit()
            return {'message': 'Post updated', 'post': post.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to update post'}, 500
    
    # Delete a post

    @jwt_required()
    @post_ns.doc('delete_post')
    def delete(self, post_id):
        """Delete a post"""
        try:
            current_user_id = int(get_jwt_identity())
            post = Post.query.get(post_id)
            
            if not post:
                return {'error': 'Post not found'}, 404
            
            if post.author_id != current_user_id:
                return {'error': 'Unauthorized'}, 403
            
            db.session.delete(post)
            db.session.commit()
            return {'message': 'Post deleted'}
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to delete post'}, 500

# Comments on a post
@post_ns.route('/<int:post_id>/comments')
class PostComments(Resource):
    @jwt_required()
    @post_ns.doc('get_comments')
    def get(self, post_id):
        """Get comments for a post"""
        post = Post.query.get(post_id)
        if not post:
            return {'error': 'Post not found'}, 404
        
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
        return {'comments': [c.to_dict() for c in comments]}
    
    # Add a comment to a post
    @jwt_required()
    @post_ns.expect(comment_model)
    @post_ns.doc('create_comment')
    def post(self, post_id):
        """Add a comment to a post"""
        try:
            current_user_id = int(get_jwt_identity())
            post = Post.query.get(post_id)
            
            if not post:
                return {'error': 'Post not found'}, 404
            
            data = request.get_json()
            
            # Validate content
            is_valid, error = validate_required_fields(data, ['content'])
            if not is_valid:
                return {'error': error}, 400
            
            content = sanitize_string(data['content'], 1000)
            is_valid, error = validate_string_length(content, 1, 1000, 'Comment')
            if not is_valid:
                return {'error': error}, 400
            
            comment = Comment(
                content=content,
                post_id=post_id,
                author_id=current_user_id
            )
            
            db.session.add(comment)
            
            # Create notification if not commenting on own post
            if post.author_id != current_user_id:
                from ..models import Notification
                user = User.query.get(current_user_id)
                if user:
                    notification = Notification(
                        user_id=post.author_id,
                        title='New Comment',
                        message=f"{user.first_name} {user.last_name} commented on your post",
                        type='comment',
                        related_id=post_id
                    )
                    db.session.add(notification)
            
            db.session.commit()
            
            # Refresh to load the author relationship
            db.session.refresh(comment)
            current_app.logger.info(f'Comment added successfully - ID: {comment.id}, Post: {post_id}')
            
            return {'message': 'Comment added', 'comment': comment.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(f'Failed to add comment: {str(e)}')
            return {'error': f'Failed to add comment: {str(e)}'}, 500

# Like and unlike a post           
@post_ns.route('/<int:post_id>/like')
class PostLike(Resource):
    @jwt_required()
    @post_ns.doc('like_post')
    def post(self, post_id):
        """Like a post"""
        try:
            from ..models import Like, Notification
            current_user_id = int(get_jwt_identity())
            
            post = Post.query.get(post_id)
            if not post:
                return {'error': 'Post not found'}, 404
            
            # Check if already liked
            existing_like = Like.query.filter_by(post_id=post_id, user_id=current_user_id).first()
            if existing_like:
                return {'message': 'Already liked', 'liked': True, 'likeCount': len(post.likes)}, 200
            
            # Create like
            like = Like(post_id=post_id, user_id=current_user_id)
            db.session.add(like)
            
            # Create notification if not liking own post
            if post.author_id != current_user_id:
                user = User.query.get(current_user_id)
                notification = Notification(
                    user_id=post.author_id,
                    title='New Like',
                    message=f"{user.first_name} {user.last_name} liked your post",
                    type='like',
                    related_id=post_id
                )
                db.session.add(notification)
            
            db.session.commit()
            return {'message': 'Post liked', 'liked': True, 'likeCount': len(post.likes)}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to like post')
            return {'error': 'Failed to like post'}, 500
    
    @jwt_required()
    @post_ns.doc('unlike_post')
    def delete(self, post_id):
        """Unlike a post"""
        try:
            from ..models import Like
            current_user_id = int(get_jwt_identity())
            
            post = Post.query.get(post_id)
            if not post:
                return {'error': 'Post not found'}, 404
            
            like = Like.query.filter_by(post_id=post_id, user_id=current_user_id).first()
            if like:
                db.session.delete(like)
                db.session.commit()
            
            return {'message': 'Post unliked', 'liked': False, 'likeCount': len(post.likes)}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to unlike post')
            return {'error': 'Failed to unlike post'}, 500
