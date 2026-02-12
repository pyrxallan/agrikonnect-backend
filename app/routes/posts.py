from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Post, Comment, User
from ..extensions import db
from ..utils.validation import (
    validate_required_fields,
    validate_string_length,
    sanitize_string,
    validate_url
)

post_ns = Namespace('posts', description='Post operations')

# Models
post_model = post_ns.model('Post', {
    'title': fields.String(required=True, description='Post title', min_length=1, max_length=255),
    'content': fields.String(required=True, description='Post content', min_length=1),
    'image_url': fields.String(description='Image URL', max_length=500),
    'community_id': fields.Integer(description='Community ID')
})

comment_model = post_ns.model('Comment', {
    'content': fields.String(required=True, description='Comment content', min_length=1, max_length=1000)
})

@post_ns.route('')
class PostList(Resource):
    @jwt_required()
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
            
            # Use eager loading to prevent N+1 queries
            query = query.options(db.joinedload(Post.author))
            
            paginated = query.order_by(Post.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'posts': [p.to_dict() for p in paginated.items],
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            return {'error': 'Failed to fetch posts'}, 500
    
    @jwt_required()
    @post_ns.expect(post_model)
    @post_ns.doc('create_post')
    def post(self):
        """Create a new post"""
        try:
            data = request.get_json()
            current_user_id = get_jwt_identity()
            
            # Validate required fields
            is_valid, error = validate_required_fields(data, ['title', 'content'])
            if not is_valid:
                return {'error': error}, 400
            
            # Sanitize and validate title
            title = sanitize_string(data.get('title'), 255)
            is_valid, error = validate_string_length(title, 1, 255, 'Title')
            if not is_valid:
                return {'error': error}, 400
            
            # Sanitize and validate content
            content = sanitize_string(data.get('content'))
            is_valid, error = validate_string_length(content, 1, None, 'Content')
            if not is_valid:
                return {'error': error}, 400
            
            # Validate image URL if provided
            image_url = data.get('image_url')
            if image_url:
                image_url = sanitize_string(image_url, 500)
                if not validate_url(image_url):
                    return {'error': 'Invalid image URL format'}, 400
            
            # Create post
            post = Post(
                title=title,
                content=content,
                image_url=image_url,
                author_id=int(current_user_id),
                community_id=data.get('community_id')
            )
            
            db.session.add(post)
            db.session.commit()
            
            return {'message': 'Post created', 'post': post.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
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
    
    @jwt_required()
    @post_ns.expect(comment_model)
    @post_ns.doc('create_comment')
    def post(self, post_id):
        """Add a comment to a post"""
        try:
            current_user_id = get_jwt_identity()
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
                author_id=int(current_user_id)
            )
            
            db.session.add(comment)
            db.session.commit()
            
            return {'message': 'Comment added', 'comment': comment.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to add comment'}, 500
