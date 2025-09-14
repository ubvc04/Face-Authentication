"""
Demo script to test Face Auth application functionality.
This script demonstrates the complete flow without requiring a frontend.
"""
import os
import sys
import json
import base64
import requests
from io import BytesIO
from PIL import Image, ImageDraw
import numpy as np

# Add the backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app, db
from app.models import User
from app.services.face_recognition import face_service

# Configuration
API_BASE_URL = 'http://localhost:5000/api'
TEST_USER_DATA = {
    'name': 'Demo User',
    'email': 'demo@example.com',
    'password': 'demopass123'
}

def create_dummy_face_image():
    """Create a dummy face image for testing purposes."""
    # Create a simple face-like image
    img = Image.new('RGB', (160, 160), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple face
    # Head outline
    draw.ellipse([20, 20, 140, 140], fill='peachpuff', outline='black')
    
    # Eyes
    draw.ellipse([45, 55, 65, 75], fill='white', outline='black')
    draw.ellipse([95, 55, 115, 75], fill='white', outline='black')
    draw.ellipse([50, 60, 60, 70], fill='black')
    draw.ellipse([100, 60, 110, 70], fill='black')
    
    # Nose
    draw.polygon([(80, 75), (75, 95), (85, 95)], fill='peachpuff', outline='black')
    
    # Mouth
    draw.arc([65, 95, 95, 115], 0, 180, fill='black', width=2)
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_data = buffer.getvalue()
    
    # Create data URL
    base64_data = base64.b64encode(img_data).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_data}"

def test_face_recognition_service():
    """Test the face recognition service directly."""
    print("🧪 Testing Face Recognition Service...")
    
    try:
        # Create dummy face image
        face_image = create_dummy_face_image()
        
        # Test face embedding extraction
        embedding, error = face_service.get_face_embedding(face_image)
        
        if embedding is not None:
            print(f"✅ Face embedding extracted successfully! Shape: {embedding.shape}")
            
            # Test face comparison with itself (should match)
            distance = face_service.compare_embeddings(embedding, embedding)
            is_same = face_service.is_same_person(embedding, embedding)
            
            print(f"✅ Face comparison test - Distance: {distance:.4f}, Same person: {is_same}")
            
            return embedding
        else:
            print(f"❌ Face embedding extraction failed: {error}")
            return None
            
    except Exception as e:
        print(f"❌ Face recognition service test failed: {e}")
        return None

def test_api_signup(face_image_data):
    """Test the signup API endpoint."""
    print("\n📝 Testing Signup API...")
    
    try:
        signup_data = {
            **TEST_USER_DATA,
            'face_image': face_image_data
        }
        
        response = requests.post(f'{API_BASE_URL}/auth/signup', json=signup_data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Signup successful: {result['message']}")
            return result
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"❌ Signup failed: {error}")
            return None
            
    except Exception as e:
        print(f"❌ Signup API test failed: {e}")
        return None

def test_api_login(face_image_data):
    """Test the login API endpoint."""
    print("\n🔐 Testing Login API...")
    
    try:
        login_data = {
            'email': TEST_USER_DATA['email'],
            'face_image': face_image_data
        }
        
        # Create a session to maintain cookies
        session = requests.Session()
        response = session.post(f'{API_BASE_URL}/auth/login', json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login successful: {result['message']}")
            print(f"   User: {result['user']['name']} ({result['user']['email']})")
            
            # Test authenticated endpoint
            me_response = session.get(f'{API_BASE_URL}/auth/me')
            if me_response.status_code == 200:
                print("✅ Authenticated endpoint access successful")
            
            return result
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"❌ Login failed: {error}")
            return None
            
    except Exception as e:
        print(f"❌ Login API test failed: {e}")
        return None

def test_database_operations():
    """Test database operations directly."""
    print("\n🗄️ Testing Database Operations...")
    
    try:
        app = create_app()
        
        with app.app_context():
            # Check if test user exists
            user = User.query.filter_by(email=TEST_USER_DATA['email']).first()
            
            if user:
                print(f"✅ Test user found in database:")
                print(f"   ID: {user.id}")
                print(f"   Name: {user.name}")
                print(f"   Email: {user.email}")
                print(f"   Verified: {user.is_verified}")
                print(f"   Created: {user.created_at}")
                print(f"   Has embedding: {len(user.embedding) if user.embedding else 0} chars")
                
                # Test embedding retrieval
                try:
                    embedding = user.get_embedding()
                    print(f"✅ Embedding retrieved successfully! Shape: {embedding.shape}")
                except Exception as e:
                    print(f"❌ Embedding retrieval failed: {e}")
                
                return user
            else:
                print("❌ Test user not found in database")
                return None
                
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return None

def create_test_user_directly():
    """Create a test user directly in the database."""
    print("\n👤 Creating Test User Directly...")
    
    try:
        app = create_app()
        
        with app.app_context():
            # Check if user already exists
            existing_user = User.query.filter_by(email=TEST_USER_DATA['email']).first()
            if existing_user:
                print("ℹ️ Test user already exists, removing...")
                db.session.delete(existing_user)
                db.session.commit()
            
            # Create dummy face image and extract embedding
            face_image = create_dummy_face_image()
            embedding, error = face_service.get_face_embedding(face_image)
            
            if embedding is None:
                print(f"❌ Cannot create user without valid face embedding: {error}")
                return None
            
            # Create new user
            from app.utils.auth_utils import hash_password
            
            user = User(
                name=TEST_USER_DATA['name'],
                email=TEST_USER_DATA['email'],
                password_hash=hash_password(TEST_USER_DATA['password']),
                is_verified=True  # Skip OTP verification for demo
            )
            
            user.set_embedding(embedding)
            
            db.session.add(user)
            db.session.commit()
            
            print(f"✅ Test user created successfully! ID: {user.id}")
            return user
            
    except Exception as e:
        print(f"❌ Test user creation failed: {e}")
        return None

def test_face_uniqueness():
    """Test face uniqueness validation."""
    print("\n🔍 Testing Face Uniqueness...")
    
    try:
        app = create_app()
        
        with app.app_context():
            # Get all users
            users = User.query.all()
            print(f"Found {len(users)} users in database")
            
            if len(users) < 1:
                print("❌ Need at least one user to test face uniqueness")
                return False
            
            # Create a new face image
            new_face_image = create_dummy_face_image()
            new_embedding, error = face_service.get_face_embedding(new_face_image)
            
            if new_embedding is None:
                print(f"❌ Cannot extract embedding from new face: {error}")
                return False
            
            # Check against existing faces
            for user in users:
                try:
                    existing_embedding = user.get_embedding()
                    distance = face_service.compare_embeddings(new_embedding, existing_embedding)
                    is_same = face_service.is_same_person(new_embedding, existing_embedding)
                    
                    print(f"   User {user.email}: distance={distance:.4f}, same={is_same}")
                    
                except Exception as e:
                    print(f"   Error comparing with user {user.email}: {e}")
            
            print("✅ Face uniqueness test completed")
            return True
            
    except Exception as e:
        print(f"❌ Face uniqueness test failed: {e}")
        return False

def cleanup_test_data():
    """Clean up test data from database."""
    print("\n🧹 Cleaning up test data...")
    
    try:
        app = create_app()
        
        with app.app_context():
            test_user = User.query.filter_by(email=TEST_USER_DATA['email']).first()
            
            if test_user:
                db.session.delete(test_user)
                db.session.commit()
                print("✅ Test user removed from database")
            else:
                print("ℹ️ No test user found to remove")
                
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    """Run the complete demo script."""
    print("🚀 Face Auth Demo Script")
    print("=" * 50)
    
    # Test 1: Face Recognition Service
    face_image = create_dummy_face_image()
    embedding = test_face_recognition_service()
    
    if embedding is None:
        print("❌ Face recognition service failed. Cannot continue.")
        return
    
    # Test 2: Database Operations
    test_database_operations()
    
    # Test 3: Create Test User Directly
    test_user = create_test_user_directly()
    
    if test_user is None:
        print("❌ Cannot create test user. Cannot continue with API tests.")
        return
    
    # Test 4: Face Uniqueness
    test_face_uniqueness()
    
    # Test 5: API Tests (requires server to be running)
    print("\n🌐 Testing API Endpoints...")
    print("Note: These tests require the Flask server to be running on localhost:5000")
    
    try:
        # Test server availability
        response = requests.get(f'{API_BASE_URL}/auth/me', timeout=5)
        server_running = True
    except:
        server_running = False
        print("⚠️ Flask server not running. Skipping API tests.")
        print("   To run API tests, start the server with: python backend/run.py")
    
    if server_running:
        # Note: Signup will fail because user already exists, but that's expected
        print("\nTesting signup (expected to fail - user already exists)...")
        test_api_signup(face_image)
        
        print("\nTesting login...")
        test_api_login(face_image)
    
    # Test 6: Cleanup
    print("\nDo you want to clean up test data? (y/n): ", end="")
    try:
        choice = input().lower().strip()
        if choice == 'y':
            cleanup_test_data()
        else:
            print("ℹ️ Test data preserved")
    except:
        print("\nℹ️ Test data preserved")
    
    print("\n✅ Demo script completed!")
    print("\nTo test the full application:")
    print("1. Start backend: cd backend && python run.py")
    print("2. Start frontend: cd frontend && npm start")
    print("3. Open http://localhost:3000 in your browser")

if __name__ == '__main__':
    main()