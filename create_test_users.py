from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check existing users
    existing = User.query.count()
    print(f"Existing users: {existing}")
    
    if existing < 3:
        # Create test users
        test_users = [
            {'email': 'farmer1@test.com', 'password': 'password123', 'first_name': 'John', 'last_name': 'Farmer', 'role': 'farmer'},
            {'email': 'farmer2@test.com', 'password': 'password123', 'first_name': 'Jane', 'last_name': 'Smith', 'role': 'farmer'},
            {'email': 'expert1@test.com', 'password': 'password123', 'first_name': 'Dr. Sarah', 'last_name': 'Expert', 'role': 'expert'},
            {'email': 'expert2@test.com', 'password': 'password123', 'first_name': 'Prof. Mike', 'last_name': 'Johnson', 'role': 'expert'},
        ]
        
        for user_data in test_users:
            if not User.query.filter_by(email=user_data['email']).first():
                user = User(
                    email=user_data['email'],
                    password=generate_password_hash(user_data['password']),
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role']
                )
                db.session.add(user)
                print(f"Created: {user_data['email']}")
        
        db.session.commit()
        print(f"\nTotal users now: {User.query.count()}")
    else:
        print("\nAll users:")
        for u in User.query.all():
            print(f"  - {u.first_name} {u.last_name} ({u.email}) - {u.role}")
