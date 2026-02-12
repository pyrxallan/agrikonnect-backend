from flask_restx import Namespace, Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import os

from ..extensions import db
from ..models import Post, Like, Comment, User

post_ns = Namespace('posts', description='Post related operations')

# --- Helper Functions ---

def save_upload_file(file, user_id):
    """Handles file saving logic and returns the relative URL."""
    if not file or not file.filename:
        return None
    
    filename = secure_filename(f"{user_id}_{file.filename}")
    upload_dir = os.path.join('uploads', 'posts')
    
    # Create directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    return f"/{file_path}"

def get_author_data(user_id):
    """Fetches user data safely for attachment to posts/comments."""
    author = User.query.get(user_id)
    if not author:
        return None
    return {
        'id': author.id,
        'first_name': author.first_name,
        'last_name': author.last_name,
        'profile_image': author.profile_image
    }

def format_post_response(post, current_user_id=None):
    """Serializes a post object and adds metadata like author and like status."""
    data = post.to_dict()
    
    # Add Like Status
    is_liked = False
    if current_user_id:
        is_liked = Like.query.filter_by(
            post_id=post.id, 
            user_id=int(current_user_id)
        ).first() is not None
    
    data['is_liked'] = is_liked
    
    # Add Author Data (respecting anonymity)
    if post.is_anonymous:
        data['author'] = {'name': 'Anonymous'}
    else:
        data['author'] = get_author_data(post.author_id)
        
    return data

# --- Resources ---

@post_ns.route('')
class PostListResource(Resource):
    @jwt_required()
    def get(self):
        """
        Fetch posts. 
        Supports pagination and filtering by author.
        """
        current_user_id = int(get_jwt_identity())
        
        # Pagination params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        author_id = request.args.get('author_id', type=int)
        
        query = Post.query
        
        if author_id:
            query = query.filter_by(author_id=author_id)
            
        # Order by newest first and paginate
        pagination = query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        posts = pagination.items
        result = [format_post_response(p, current_user_id) for p in posts]
        
        return {
            'posts': result,
            'page': page,
            'total_pages': pagination.pages,
            'has_next': pagination.has_next
        }

    @jwt_required()
    def post(self):
        """Create a new post (supports both JSON and Multipart/Form-data)."""
        user_id = int(get_jwt_identity())
        
        content, title, is_anonymous, image_url = None, None, False, None

        # Check for multipart form data (file upload)
        if 'image' in request.files:
            content = request.form.get('content')
            title = request.form.get('title')
            is_anonymous = request.form.get('is_anonymous', 'false').lower() == 'true'
            
            image_file = request.files['image']
            image_url = save_upload_file(image_file, user_id)
            
        else:
            # Fallback to JSON body
            data = request.get_json()
            if not data:
                post_ns.abort(400, 'Request payload is required')
            
            content = data.get('content')
            title = data.get('title')
            is_anonymous = data.get('is_anonymous', False)
            image_url = data.get('image_url')

        # Validation
        if not content or not content.strip():
            post_ns.abort(400, 'Content cannot be empty')

        new_post = Post(
            title=title,
            content=content,
            image_url=image_url,
            is_anonymous=is_anonymous,
            author_id=user_id
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return {
            'message': 'Post created successfully',
            'post': format_post_response(new_post, user_id)
        }, 201


@post_ns.route('/<int:post_id>')
class PostDetailResource(Resource):
    @jwt_required(optional=True)
    def get(self, post_id):
        """Retrieve a single post details."""
        post = Post.query.get_or_404(post_id)
        current_user = get_jwt_identity()
        
        return format_post_response(post, current_user)

    @jwt_required()
    def delete(self, post_id):
        """Delete a post (Only author allowed)."""
        user_id = int(get_jwt_identity())
        post = Post.query.get_or_404(post_id)
        
        if post.author_id != user_id:
            post_ns.abort(403, 'You are not authorized to delete this post')
            
        db.session.delete(post)
        db.session.commit()
        
        return {'message': 'Post deleted'}, 200


@post_ns.route('/<int:post_id>/like')
class LikeToggleResource(Resource):
    @jwt_required()
    def post(self, post_id):
        """Like a post."""
        user_id = int(get_jwt_identity())
        post = Post.query.get_or_404(post_id)
        
        # Check existence
        exists = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        if exists:
            return {'message': 'Already liked', 'liked': True}, 200
            
        db.session.add(Like(post_id=post_id, user_id=user_id))
        db.session.commit()
        
        return {'message': 'Post liked', 'liked': True}, 201

    @jwt_required()
    def delete(self, post_id):
        """Unlike a post."""
        user_id = int(get_jwt_identity())
        
        like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        if not like:
            return {'message': 'Post not liked yet', 'liked': False}, 200
            
        db.session.delete(like)
        db.session.commit()
        
        return {'message': 'Post unliked', 'liked': False}, 200


@post_ns.route('/<int:post_id>/comments')
class CommentListResource(Resource):
    @jwt_required()
    def get(self, post_id):
        """Get comments for a post."""
        Post.query.get_or_404(post_id) # Ensure post exists
        
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
        
        result = []
        for c in comments:
            data = c.to_dict()
            data['author'] = get_author_data(c.author_id)
            result.append(data)
            
        return {'comments': result}

    @jwt_required()
    def post(self, post_id):
        """Add a comment to a post."""
        user_id = int(get_jwt_identity())
        Post.query.get_or_404(post_id) # Ensure post exists
        
        data = request.get_json()
        text = data.get('content')
        
        if not text or not text.strip():
            post_ns.abort(400, 'Comment content is required')
            
        new_comment = Comment(content=text, post_id=post_id, author_id=user_id)
        db.session.add(new_comment)
        db.session.commit()
        
        response = new_comment.to_dict()
        response['author'] = get_author_data(user_id)
        
        return response, 201


@post_ns.route('/<int:post_id>/comments/<int:comment_id>')
class CommentDetailResource(Resource):
    @jwt_required()
    def delete(self, post_id, comment_id):
        """Delete a comment."""
        user_id = int(get_jwt_identity())
        
        # Verify post exists
        Post.query.get_or_404(post_id)
        
        comment = Comment.query.get_or_404(comment_id)
        
        # Verify ownership
        if comment.author_id != user_id:
            post_ns.abort(403, 'You can only delete your own comments')
            
        db.session.delete(comment)
        db.session.commit()
        
        return {'message': 'Comment removed'}, 200
