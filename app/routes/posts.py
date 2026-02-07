import os
import uuid
from typing import Optional
from urllib.parse import urljoin

from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Comment, Post, User
from ..models.post_like import PostLike

# Define the namespace for posts
posts_ns = Namespace('posts', description='Operations related to posts')
post_ns = posts_ns

#constats
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

#swagger docs response models
post_model = posts_ns.model('Post', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a post'),
    'title': fields.String(required=True, description='The title of the post'),
    'content': fields.String(required=True, description='The content of the post'),
    'author_id': fields.Integer(required=True, description='The ID of the post author'),
    'created_at': fields.DateTime(description='The date and time the post was created'),
    'updated_at': fields.DateTime(description='The date and time the post was last updated'),
})

author_model = posts_ns.model('Author', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of the author'),
    'first_name': fields.String(description='The first name of the author'),
    'last_name': fields.String(description='The last name of the author'),
})

Comment_model = posts_ns.model('Comment', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a comment'),
    'content': fields.String(required=True, description='The content of the comment'),  
    'author_id': fields.Integer(required=True, description='The ID of the comment author'),
    'post_id': fields.Integer(required=True, description='The ID of the post the comment belongs to'),
    'created_at': fields.DateTime(description='The date and time the comment was created'),
    'updated_at': fields.DateTime(description='The date and time the comment was last updated'),
})

create_post_model = posts_ns.model('CreatePost', {
    'title': fields.String(required=True, description='The title of the post'),
    'content': fields.String(required=True, description='The content of the post'),
})

create_comment_model = posts_ns.model('CreateComment', {
    'content': fields.String(required=True, description='The content of the comment'),
})  

#helper function to check allowed file extensions
def _is_allowed_image(filename: str) -> bool:
    """Check if file has an allowed image extension"""
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _is_valid_image(file) -> bool:
    """Check if the uploaded file is a valid image and within size limits"""
    if file and _is_allowed_image(file.filename):
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)  # Reset file pointer after checking size
        return file_length <= MAX_CONTENT_LENGTH
    return False

#get file size by seeking to the end of the file and getting the position
def _get_file_size(file) -> int:
    """Get the size of the uploaded file"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer after getting size
    return size


def _save_image(file) -> Optional[str]:
    """Save the uploaded image to the server and return its URL"""
    if not _is_valid_image(file):
        raise RequestEntityTooLarge('File is too large or has an invalid format')
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_filename)
    
    file.save(file_path)
    
    # Return the URL to access the uploaded image
    return urljoin(request.host_url, f"{upload_folder}/{unique_filename}")

def save_image(file) -> Optional[str]:
    """Wrapper function to save image and handle exceptions"""
    try:
        return _save_image(file)
    except RequestEntityTooLarge as e:
        posts_ns.abort(413, str(e))
    except Exception as e:
        posts_ns.abort(500, f"An error occurred while saving the image: {str(e)}")
    return None


def _image_url(file_storage) -> Optional[str]:
    """Validate and save the uploaded image, returning its URL"""
    if file_storage and _is_allowed_image(file_storage.filename):
        return save_image(file_storage)
    return None


def _author_payload(user: User) -> dict:
    return {
        'id': user.id,
        'name': user.full_name,
    }


def _comment_payload(comment: Comment) -> dict:
    return {
        'id': comment.id,
        'content': comment.content,
        'author': _author_payload(comment.author),
        'createdAt': comment.created_at.isoformat() if comment.created_at else None,
    }


def _post_payload(post: Post, current_user_id: Optional[int] = None) -> dict:
    liked = False
    if current_user_id:
        liked = PostLike.query.filter_by(post_id=post.id, user_id=current_user_id).first() is not None

    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
    return {
        'id': post.id,
        'content': post.content,
        'imageUrl': post.image_url or None,
        'author': _author_payload(post.author),
        'createdAt': post.created_at.isoformat() if post.created_at else None,
        'likeCount': PostLike.query.filter_by(post_id=post.id).count(),
        'isLiked': liked,
        'comments': [_comment_payload(comment) for comment in comments],
    }

#Add the actual route classes/endpoints (GET/POST /posts, like/unlike, comments) because this file currently only defines helpers and no route
@posts_ns.route('')
class PostListResource(Resource):
    @jwt_required(optional=True)
    def get(self):
        """Get paginated posts"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('perPage', 10, type=int)
        current_user_id = get_jwt_identity()
        current_user_id = int(current_user_id) if current_user_id is not None else None

        pagination = Post.query.order_by(Post.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        posts = [_post_payload(post, current_user_id) for post in pagination.items]
        return {
            'posts': posts,
            'page': page,
            'totalPages': pagination.pages or 1
        }, 200

    @jwt_required()
    def post(self):
        """Create a new post (multipart form)"""
        current_user_id = int(get_jwt_identity())
        author = User.query.get(current_user_id)
        if not author:
            return {'message': 'User not found'}, 404

        content = request.form.get('content') or request.form.get('body')
        if not content:
            return {'message': 'content is required'}, 400

        image_file = request.files.get('image')
        image_url = _image_url(image_file)

        title = content.strip()[:200] if content.strip() else 'Post'

        post = Post(title=title, content=content, image_url=image_url, author_id=author.id)
        db.session.add(post)
        db.session.commit()

        return _post_payload(post, current_user_id), 201
    
#get post by id, update post, delete post
@posts_ns.route('/<int:post_id>')
class PostResource(Resource):
    @jwt_required(optional=True)
    def get(self, post_id):
        """Get a post by ID"""
        current_user_id = get_jwt_identity()
        current_user_id = int(current_user_id) if current_user_id is not None else None

        post = Post.query.get(post_id)
        if not post:
            return {'message': 'Post not found'}, 404

        return _post_payload(post, current_user_id), 200

    @jwt_required()
    def delete(self, post_id):
        """Delete a post"""
        current_user_id = int(get_jwt_identity())
        post = Post.query.get(post_id)
        if not post:
            return {'message': 'Post not found'}, 404
        if post.author_id != current_user_id:
            return {'message': 'Unauthorized'}, 403
        db.session.delete(post)
        db.session.commit()
        return {'message': 'Post deleted'}, 200   

#like/unlike post, create comment for post, get comments for post
@posts_ns.route('/<int:post_id>/like')
class PostLikeResource(Resource):   
    @jwt_required()
    def post(self, post_id):
        """Like a post"""
        current_user_id = int(get_jwt_identity())
        post = Post.query.get(post_id)
        if not post:
            return {'message': 'Post not found'}, 404

        existing_like = PostLike.query.filter_by(post_id=post_id, user_id=current_user_id).first()
        if not existing_like:
            like = PostLike(user_id=current_user_id, post_id=post_id)
            db.session.add(like)
            db.session.commit()

        like_count = PostLike.query.filter_by(post_id=post_id).count()
        return {
            'id': post_id,
            'likeCount': like_count,
            'liked': True
        }, 200

   # Unlike a post by deleting the PostLike entry for the current user and post, then return the updated like count and liked status
    @jwt_required()
    def delete(self, post_id):
        """Unlike a post"""
        current_user_id = int(get_jwt_identity())
        post = Post.query.get(post_id)
        if not post:
            return {'message': 'Post not found'}, 404

        existing_like = PostLike.query.filter_by(post_id=post_id, user_id=current_user_id).first()
        if existing_like:
            db.session.delete(existing_like)
            db.session.commit()

        like_count = PostLike.query.filter_by(post_id=post_id).count()
        return {
            'id': post_id,
            'likeCount': like_count,
            'liked': False
        }, 200
   

# Create a comment for a post, get comments for a post, update comment, delete comment
@posts_ns.route('/<int:post_id>/comments')
class PostCommentResource(Resource):
    @jwt_required(optional=True)
    def get(self, post_id):
        """Get comments for a post"""
        post = Post.query.get(post_id)
        if not post:
            return {'message': 'Post not found'}, 404

        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
        return [_comment_payload(comment) for comment in comments], 200

    @jwt_required()
    def post(self, post_id):
        """Create a comment for a post"""
        current_user_id = int(get_jwt_identity())
        post = Post.query.get(post_id)
        if not post:
            return {'message': 'Post not found'}, 404

        data = request.get_json(silent=True) or {}
        content = data.get('content')
        if not content:
            return {'message': 'Content is required'}, 400

        comment = Comment(content=content, author_id=current_user_id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()

        return _comment_payload(comment), 201

 

