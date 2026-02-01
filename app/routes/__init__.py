from flask_restx import Api, Namespace, Resource

def register_routes(api: Api):
    # Import and register route modules here
    from .auth import auth_ns
    from .users import user_ns
    from .posts import post_ns
    from .communities import community_ns
    from .experts import expert_ns
    from .messages import message_ns

    # Create general API namespace
    general_ns = Namespace('general', description='General API information')

    @general_ns.route('/')
    class APIInfo(Resource):
        def get(self):
            """Get API information"""
            return {
                'name': 'Agrikonnect API',
                'version': '1.0',
                'description': 'RESTful API for Agrikonnect agricultural platform',
                'documentation': '/api/docs',
                'endpoints': {
                    'auth': '/api/v1/auth',
                    'users': '/api/v1/users',
                    'posts': '/api/v1/posts',
                    'communities': '/api/v1/communities',
                    'experts': '/api/v1/experts',
                    'messages': '/api/v1/messages'
                }
            }

    # Register namespaces
    api.add_namespace(general_ns, path='/api/v1')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(user_ns, path='/api/v1/users')
    api.add_namespace(post_ns, path='/api/v1/posts')
    api.add_namespace(community_ns, path='/api/v1/communities')
    api.add_namespace(expert_ns, path='/api/v1/experts')
    api.add_namespace(message_ns, path='/api/v1/messages')