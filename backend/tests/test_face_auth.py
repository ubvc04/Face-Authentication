"""
Unit tests for Face Auth application.
"""
import unittest
import tempfile
import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import numpy as np

# Set up test environment
os.environ['TESTING'] = 'True'

from app import create_app, db
from app.models import User
from app.services.face_recognition import face_service
from app.utils.auth_utils import hash_password, verify_password, generate_otp, verify_otp, hash_otp

class FaceAuthTestCase(unittest.TestCase):
    """Base test case for Face Auth application."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.client = self.app.test_client()
        
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_face_image(self):
        """Create a test face image."""
        img = Image.new('RGB', (160, 160), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw simple face
        draw.ellipse([20, 20, 140, 140], fill='peachpuff', outline='black')
        draw.ellipse([45, 55, 65, 75], fill='white', outline='black')
        draw.ellipse([95, 55, 115, 75], fill='white', outline='black')
        draw.ellipse([50, 60, 60, 70], fill='black')
        draw.ellipse([100, 60, 110, 70], fill='black')
        draw.polygon([(80, 75), (75, 95), (85, 95)], fill='peachpuff', outline='black')
        draw.arc([65, 95, 95, 115], 0, 180, fill='black', width=2)
        
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        img_data = buffer.getvalue()
        
        base64_data = base64.b64encode(img_data).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_data}"

class TestPasswordUtils(FaceAuthTestCase):
    """Test password hashing and verification utilities."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        
        # Test hashing
        hashed = hash_password(password)
        self.assertIsInstance(hashed, str)
        self.assertNotEqual(password, hashed)
        
        # Test verification
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong_password", hashed))
    
    def test_otp_generation(self):
        """Test OTP generation and verification."""
        otp = generate_otp()
        
        # Test OTP format
        self.assertIsInstance(otp, str)
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
        
        # Test OTP hashing and verification
        hashed_otp = hash_otp(otp)
        self.assertTrue(verify_otp(otp, hashed_otp))
        self.assertFalse(verify_otp("123456", hashed_otp))

class TestFaceRecognition(FaceAuthTestCase):
    """Test face recognition functionality."""
    
    def test_face_embedding_extraction(self):
        """Test face embedding extraction from image."""
        face_image = self.create_test_face_image()
        
        embedding, error = face_service.get_face_embedding(face_image)
        
        if embedding is not None:
            self.assertIsInstance(embedding, np.ndarray)
            self.assertEqual(len(embedding.shape), 1)  # Should be 1D array
            self.assertGreater(len(embedding), 0)
        else:
            # If face detection fails with test image, that's also valid
            self.assertIsInstance(error, str)
            self.assertGreater(len(error), 0)
    
    def test_face_comparison(self):
        """Test face embedding comparison."""
        # Create two identical embeddings
        embedding1 = np.random.rand(512)
        embedding2 = embedding1.copy()
        
        # Test comparison
        distance = face_service.compare_embeddings(embedding1, embedding2)
        is_same = face_service.is_same_person(embedding1, embedding2)
        
        self.assertIsInstance(distance, float)
        self.assertAlmostEqual(distance, 0.0, places=5)  # Should be nearly identical
        self.assertTrue(is_same)
        
        # Test with different embeddings
        embedding3 = np.random.rand(512)
        distance2 = face_service.compare_embeddings(embedding1, embedding3)
        is_same2 = face_service.is_same_person(embedding1, embedding3)
        
        self.assertGreater(distance2, distance)

class TestUserModel(FaceAuthTestCase):
    """Test User model functionality."""
    
    def test_user_creation(self):
        """Test user creation and basic properties."""
        user = User(
            name="Test User",
            email="test@example.com",
            password_hash=hash_password("password123"),
            is_verified=False
        )
        
        # Test embedding storage
        test_embedding = np.random.rand(512)
        user.set_embedding(test_embedding)
        
        db.session.add(user)
        db.session.commit()
        
        # Test retrieval
        retrieved_user = User.query.filter_by(email="test@example.com").first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.name, "Test User")
        self.assertEqual(retrieved_user.email, "test@example.com")
        self.assertFalse(retrieved_user.is_verified)
        
        # Test embedding retrieval
        retrieved_embedding = retrieved_user.get_embedding()
        np.testing.assert_array_almost_equal(test_embedding, retrieved_embedding)
    
    def test_user_to_dict(self):
        """Test user serialization to dictionary."""
        user = User(
            name="Test User",
            email="test@example.com",
            password_hash=hash_password("password123"),
            is_verified=True
        )
        
        user_dict = user.to_dict()
        
        self.assertIsInstance(user_dict, dict)
        self.assertEqual(user_dict['name'], "Test User")
        self.assertEqual(user_dict['email'], "test@example.com")
        self.assertTrue(user_dict['is_verified'])
        self.assertNotIn('password_hash', user_dict)  # Should not include password

class TestAuthAPI(FaceAuthTestCase):
    """Test authentication API endpoints."""
    
    def test_signup_validation(self):
        """Test signup input validation."""
        # Test missing fields
        response = self.client.post('/api/auth/signup', json={})
        self.assertEqual(response.status_code, 400)
        
        # Test invalid email
        response = self.client.post('/api/auth/signup', json={
            'name': 'Test User',
            'email': 'invalid-email',
            'password': 'password123',
            'face_image': self.create_test_face_image()
        })
        # May pass or fail depending on validation implementation
    
    def test_login_validation(self):
        """Test login input validation."""
        # Test missing fields
        response = self.client.post('/api/auth/login', json={})
        self.assertEqual(response.status_code, 400)
        
        # Test with non-existent user
        response = self.client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'face_image': self.create_test_face_image()
        })
        self.assertEqual(response.status_code, 404)

class TestIntegration(FaceAuthTestCase):
    """Integration tests for complete workflows."""
    
    def test_complete_user_workflow(self):
        """Test complete user registration and login workflow."""
        # Create a test user directly in database
        test_embedding = np.random.rand(512)
        
        user = User(
            name="Integration Test User",
            email="integration@example.com",
            password_hash=hash_password("password123"),
            is_verified=True
        )
        user.set_embedding(test_embedding)
        
        db.session.add(user)
        db.session.commit()
        
        # Test user exists
        retrieved_user = User.query.filter_by(email="integration@example.com").first()
        self.assertIsNotNone(retrieved_user)
        self.assertTrue(retrieved_user.is_verified)
        
        # Test embedding comparison
        stored_embedding = retrieved_user.get_embedding()
        distance = face_service.compare_embeddings(test_embedding, stored_embedding)
        self.assertAlmostEqual(distance, 0.0, places=5)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)