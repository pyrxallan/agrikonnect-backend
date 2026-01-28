from flask_restx import Api

def register_routes(api: Api):
    # Import and register route modules here
    from .auth import auth_ns
    from .users import user_ns
    from .posts import post_ns
    from .communities import community_ns
    from .experts import expert_ns
    from .messages import message_ns

    # Register namespaces
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(user_ns, path='/api/v1/users')
    api.add_namespace(post_ns, path='/api/v1/posts')
    api.add_namespace(community_ns, path='/api/v1/communities')
    api.add_namespace(expert_ns, path='/api/v1/experts')
    api.add_namespace(message_ns, path='/api/v1/messages')