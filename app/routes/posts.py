from flask_restx import Namespace, Resource
from flask import request
from flask_jwt_extended import jwt_required
from ..models import Post

post_ns = Namespace('posts', description='Post operations')

@post_ns.route('')
class PostList(Resource):
    @jwt_required()
    def get(self):
        """Get posts with optional author filter"""
        author_id = request.args.get('author_id', type=int)
        
        query = Post.query
        if author_id:
            query = query.filter_by(author_id=author_id)
        
        posts = query.order_by(Post.created_at.desc()).all()
        return {'posts': [p.to_dict() for p in posts]}
