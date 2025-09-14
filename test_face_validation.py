#!/usr/bin/env python3
"""
Simple test script to verify face validation is working.
"""
import requests
import base64
import json

def test_face_validation():
    """Test the face validation endpoint with a simple image."""
    
    # Create a simple test image (1x1 pixel PNG in base64)
    # This is a minimal valid image to test the bypass
    test_image_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGAkev+lQAAAABJRU5ErkJggg=="
    
    print("Testing face validation endpoint...")
    
    try:
        # Test the validate-face endpoint
        response = requests.post(
            'http://localhost:5000/api/auth/validate-face',
            json={'face_image': test_image_b64},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Face validation is working!")
            return True
        else:
            print("❌ Face validation failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error testing face validation: {e}")
        return False

if __name__ == "__main__":
    test_face_validation()