#!/usr/bin/env python3
"""Seed database with test data for communities and experts"""

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.community import Community
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Create expert users if they don't exist
    experts_data = [
        {
            'email': 'amina.hassan@agrikonnect.com',
            'first_name': 'Amina',
            'last_name': 'Hassan',
            'password': 'expert123',
            'role': 'expert',
            'bio': 'Soil Health & Crop Nutrition Specialist',
            'location': 'Nairobi, Kenya'
        },
        {
            'email': 'wanjiku.muthoni@agrikonnect.com',
            'first_name': 'Wanjiku',
            'last_name': 'Muthoni',
            'password': 'expert123',
            'role': 'expert',
            'bio': 'Sustainable Agriculture & Climate Adaptation Expert',
            'location': 'Nakuru, Kenya'
        },
        {
            'email': 'emmanuel.banda@agrikonnect.com',
            'first_name': 'Emmanuel',
            'last_name': 'Banda',
            'password': 'expert123',
            'role': 'expert',
            'bio': 'Pest Management & Organic Farming Consultant',
            'location': 'Eldoret, Kenya'
        }
    ]
    
    for expert_data in experts_data:
        if not User.query.filter_by(email=expert_data['email']).first():
            expert = User(
                email=expert_data['email'],
                first_name=expert_data['first_name'],
                last_name=expert_data['last_name'],
                password=generate_password_hash(expert_data['password']),
                role=expert_data['role'],
                bio=expert_data['bio'],
                location=expert_data['location']
            )
            db.session.add(expert)
            print(f"Created expert: {expert.full_name}")
    
    db.session.commit()
    
    # Get or create a farmer user for community creation
    farmer = User.query.filter_by(role='farmer').first()
    if not farmer:
        farmer = User(
            email='farmer@test.com',
            first_name='Test',
            last_name='Farmer',
            password=generate_password_hash('farmer123'),
            role='farmer',
            location='Kenya'
        )
        db.session.add(farmer)
        db.session.commit()
        print(f"Created farmer: {farmer.full_name}")
    
    # Create communities if they don't exist
    communities_data = [
        {'name': 'Soil Management', 'description': 'Tips and discussions about soil health and management'},
        {'name': 'Organic Farming', 'description': 'Sustainable and organic farming practices'},
        {'name': 'Pest Control', 'description': 'Natural and effective pest control methods'},
        {'name': 'Irrigation', 'description': 'Water management and irrigation techniques'},
        {'name': 'Climate Smart Agriculture', 'description': 'Adapting farming to climate change'},
        {'name': 'Crop Rotation', 'description': 'Best practices for crop rotation and soil fertility'}
    ]
    
    for comm_data in communities_data:
        if not Community.query.filter_by(name=comm_data['name']).first():
            community = Community(
                name=comm_data['name'],
                description=comm_data['description'],
                creator_id=farmer.id
            )
            db.session.add(community)
            community.members.append(farmer)
            print(f"Created community: {community.name}")
    
    db.session.commit()
    print("\nDatabase seeded successfully!")
