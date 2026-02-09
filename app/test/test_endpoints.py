#!/usr/bin/env python3
"""Test communities and experts endpoints"""

import requests
import json

BASE_URL = 'http://localhost:5000/api/v1'

# Test data
test_user = {
    'email': 'test@example.com',
    'password': 'test123',
    'first_name': 'Test',
    'last_name': 'User',
    'role': 'farmer'
}

def test_endpoints():
    print(" Testing Communities and Experts Endpoints\n")
    
    # Register or login
    print("1. Authenticating...")
    try:
        response = requests.post(f'{BASE_URL}/auth/register', json=test_user)
        if response.status_code == 201:
            print(" Registered new user")
        else:
            response = requests.post(f'{BASE_URL}/auth/login', json={
                'email': test_user['email'],
                'password': test_user['password']
            })
            print(" Logged in existing user")
        
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
    except Exception as e:
        print(f" Authentication failed: {e}")
        return
    
    # Test Communities
    print("\n2. Testing Communities...")
    try:
        response = requests.get(f'{BASE_URL}/communities', headers=headers)
        communities = response.json()
        print(f" GET /communities - Found {len(communities)} communities")
        
        if communities:
            comm_id = communities[0]['id']
            response = requests.get(f'{BASE_URL}/communities/{comm_id}', headers=headers)
            print(f" GET /communities/{comm_id} - {response.json()['name']}")
            
            response = requests.post(f'{BASE_URL}/communities/{comm_id}/join', headers=headers)
            print(f" POST /communities/{comm_id}/join - {response.json()['message']}")
    except Exception as e:
        print(f" Communities test failed: {e}")
    
    # Test Experts
    print("\n3. Testing Experts...")
    try:
        response = requests.get(f'{BASE_URL}/experts', headers=headers)
        experts = response.json()
        print(f" GET /experts - Found {len(experts)} experts")
        
        if experts:
            expert_id = experts[0]['id']
            response = requests.get(f'{BASE_URL}/experts/{expert_id}', headers=headers)
            print(f" GET /experts/{expert_id} - {response.json()['name']}")
            
            response = requests.post(f'{BASE_URL}/experts/{expert_id}/follow', headers=headers)
            print(f" POST /experts/{expert_id}/follow - {response.json()['message']}")
    except Exception as e:
        print(f" Experts test failed: {e}")
    
    print("\n All tests completed!")

if __name__ == '__main__':
    test_endpoints()
