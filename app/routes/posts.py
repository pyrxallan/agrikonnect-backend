from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required
from ..models import Post

post_ns = Namespace('posts', description='Post operations')

@post_ns.route('')
class PostListResource(Resource):
    @jwt_required()
    @post_ns.doc('list_posts', params={
        'page': 'Page number (default: 1)',
        'per_page': 'Items per page (default: 20, max: 100)',
        'author_id': 'Filter by author ID'
    })
    def get(self):
        """Get posts with optional author filter"""
        author_id = request.args.get('author_id', type=int)
        
        query = Post.query
        if author_id:
            query = query.filter_by(author_id=author_id)
        
        posts = query.order_by(Post.created_at.desc()).all()
        return {'posts': [p.to_dict() for p in posts]}
