#!/usr/bin/env python3
"""
Comprehensive test script for face authentication debugging.
This script will test each component of the face validation pipeline.
"""
import os
import sys
import base64
import requests
import json
from PIL import Image
import io
import sqlite3

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_test_image():
    """Create a simple test image with a face-like pattern."""
    # Create a 300x300 RGB image with a simple face pattern
    img = Image.new('RGB', (300, 300), color='white')
    pixels = img.load()
    
    # Draw a simple face pattern
    # Face outline (circle)
    center_x, center_y = 150, 150
    radius = 80
    
    for x in range(300):
        for y in range(300):
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            
            # Face outline
            if abs(distance - radius) < 3:
                pixels[x, y] = (0, 0, 0)
            
            # Eyes
            elif ((x - 120) ** 2 + (y - 120) ** 2) < 100:  # Left eye
                pixels[x, y] = (0, 0, 0)
            elif ((x - 180) ** 2 + (y - 120) ** 2) < 100:  # Right eye
                pixels[x, y] = (0, 0, 0)
            
            # Mouth
            elif ((x - 150) ** 2 + (y - 180) ** 2) < 200 and y > 170:
                pixels[x, y] = (0, 0, 0)
    
    return img

def image_to_base64(image):
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    return base64.b64encode(img_data).decode('utf-8')

def test_image_conversion():
    """Test image creation and base64 conversion."""
    print("=" * 50)
    print("STEP 1: Testing Image Creation and Conversion")
    print("=" * 50)
    
    try:
        # Create test image
        test_img = create_test_image()
        print(f"✅ Created test image: {test_img.size}, {test_img.mode}")
        
        # Convert to base64
        img_b64 = image_to_base64(test_img)
        print(f"✅ Converted to base64: {len(img_b64)} characters")
        
        # Create data URL
        data_url = f"data:image/png;base64,{img_b64}"
        print(f"✅ Created data URL: {len(data_url)} characters")
        
        # Save test image for manual inspection
        test_img.save("test_face_image.png")
        print("✅ Saved test image as 'test_face_image.png'")
        
        return data_url
        
    except Exception as e:
        print(f"❌ Image creation failed: {e}")
        return None

def test_face_service_directly():
    """Test the face recognition service directly."""
    print("\n" + "=" * 50)
    print("STEP 2: Testing Face Recognition Service Directly")
    print("=" * 50)
    
    try:
        # Import face service
        from app.services.face_recognition import face_service
        print("✅ Successfully imported face_service")
        
        # Create test image
        test_img = create_test_image()
        img_b64_data = f"data:image/png;base64,{image_to_base64(test_img)}"
        
        # Test base64 to image conversion
        print("\nTesting base64 to image conversion...")
        pil_image = face_service.base64_to_image(img_b64_data)
        if pil_image:
            print(f"✅ Base64 to PIL conversion: {pil_image.size}, {pil_image.mode}")
        else:
            print("❌ Base64 to PIL conversion failed")
            return False
        
        # Test face detection
        print("\nTesting face detection...")
        face_tensor = face_service.detect_and_extract_face(pil_image)
        if face_tensor is not None:
            print(f"✅ Face detection successful: {face_tensor.shape}")
        else:
            print("❌ Face detection failed")
            
        # Test embedding generation
        if face_tensor is not None:
            print("\nTesting embedding generation...")
            embedding = face_service.generate_embedding(face_tensor)
            if embedding is not None:
                print(f"✅ Embedding generation successful: {embedding.shape}")
            else:
                print("❌ Embedding generation failed")
        
        # Test full pipeline
        print("\nTesting full pipeline...")
        embedding, error_msg = face_service.get_face_embedding(img_b64_data)
        if embedding is not None:
            print(f"✅ Full pipeline successful: {embedding.shape}")
            print(f"   Embedding preview: {embedding[:5]}...")
            return True
        else:
            print(f"❌ Full pipeline failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Face service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test the face validation API endpoint."""
    print("\n" + "=" * 50)
    print("STEP 3: Testing API Endpoint")
    print("=" * 50)
    
    try:
        # Create test image
        test_img = create_test_image()
        img_data_url = f"data:image/png;base64,{image_to_base64(test_img)}"
        
        # Test validate-face endpoint
        print("Testing /api/auth/validate-face endpoint...")
        response = requests.post(
            'http://localhost:5000/api/auth/validate-face',
            json={'face_image': img_data_url},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('valid'):
                print("✅ API endpoint validation successful")
                return True
            else:
                print(f"❌ API validation failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API endpoint failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server at localhost:5000")
        print("   Make sure the backend server is running")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_database_operations():
    """Test database operations for user registration."""
    print("\n" + "=" * 50)
    print("STEP 4: Testing Database Operations")
    print("=" * 50)
    
    try:
        # Test database connection
        db_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'face_auth.db')
        print(f"Database path: {db_path}")
        
        if os.path.exists(db_path):
            print("✅ Database file exists")
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            if cursor.fetchone():
                print("✅ Users table exists")
                
                # Check table structure
                cursor.execute("PRAGMA table_info(users);")
                columns = cursor.fetchall()
                print(f"✅ Table columns: {[col[1] for col in columns]}")
                
                # Count existing users
                cursor.execute("SELECT COUNT(*) FROM users;")
                user_count = cursor.fetchone()[0]
                print(f"✅ Current user count: {user_count}")
                
            else:
                print("❌ Users table does not exist")
                return False
                
            conn.close()
            return True
            
        else:
            print("❌ Database file does not exist")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_full_registration_flow():
    """Test the complete user registration flow."""
    print("\n" + "=" * 50)
    print("STEP 5: Testing Full Registration Flow")
    print("=" * 50)
    
    try:
        # Create test user data
        test_user = {
            "name": "Test User",
            "email": f"test_user_{os.urandom(4).hex()}@example.com",
            "password": "Test123!@#"
        }
        
        # Create test image
        test_img = create_test_image()
        img_data_url = f"data:image/png;base64,{image_to_base64(test_img)}"
        
        # Step 1: Validate face
        print("Step 1: Validating face...")
        validate_response = requests.post(
            'http://localhost:5000/api/auth/validate-face',
            json={'face_image': img_data_url},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if validate_response.status_code != 200:
            print(f"❌ Face validation failed: {validate_response.text}")
            return False
        
        validate_result = validate_response.json()
        if not validate_result.get('valid'):
            print(f"❌ Face not valid: {validate_result.get('message')}")
            return False
        
        print("✅ Face validation successful")
        
        # Step 2: Register user
        print("Step 2: Registering user...")
        register_data = {
            **test_user,
            'face_image': img_data_url
        }
        
        register_response = requests.post(
            'http://localhost:5000/api/auth/signup',
            json=register_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Registration status: {register_response.status_code}")
        print(f"Registration response: {register_response.text}")
        
        if register_response.status_code == 201:
            print("✅ User registration successful")
            return True
        else:
            print(f"❌ User registration failed")
            return False
            
    except Exception as e:
        print(f"❌ Full registration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 FACE AUTHENTICATION DEBUG TEST SUITE")
    print("=" * 60)
    
    # Set development bypass
    os.environ['DEV_FACE_BYPASS'] = 'true'
    print("🔧 Development bypass enabled")
    
    results = []
    
    # Run tests
    results.append(("Image Creation", test_image_conversion()))
    results.append(("Face Service", test_face_service_directly()))
    results.append(("API Endpoint", test_api_endpoint()))
    results.append(("Database", test_database_operations()))
    results.append(("Full Registration", test_full_registration_flow()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} : {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print("🚨 Some tests failed. Check the output above for details.")
    
    # Cleanup
    try:
        if os.path.exists("test_face_image.png"):
            os.remove("test_face_image.png")
            print("\n🧹 Cleaned up test files")
    except:
        pass

if __name__ == "__main__":
    main()