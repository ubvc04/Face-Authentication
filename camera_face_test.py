#!/usr/bin/env python3
"""
Camera Face Capture and Validation Test
This script will:
1. Capture your face using the camera
2. Test face validation step by step
3. Save the image to database if successful
4. Show detailed debugging information
"""

import cv2
import numpy as np
import base64
import requests
import json
import time
import os
from PIL import Image
import io

class CameraFaceTest:
    def __init__(self):
        self.api_base = "http://localhost:5000/api"
        self.captured_image = None
        self.captured_base64 = None
        
    def capture_face_from_camera(self):
        """Capture face image from camera with preview."""
        print("🎥 STARTING CAMERA FACE CAPTURE")
        print("=" * 50)
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open camera")
            return False
            
        # Set camera properties for better quality
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("📸 Camera opened successfully")
        print("Instructions:")
        print("- Look directly at the camera")
        print("- Ensure good lighting")
        print("- Press SPACE to capture")
        print("- Press ESC to cancel")
        print("\nCamera preview starting...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to grab frame")
                break
                
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Add instructions overlay
            cv2.putText(frame, "Press SPACE to capture, ESC to cancel", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Look directly at camera", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Face Capture - Press SPACE to capture', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                print("❌ Capture cancelled by user")
                cap.release()
                cv2.destroyAllWindows()
                return False
            elif key == 32:  # SPACE key
                # Capture the image
                self.captured_image = frame.copy()
                print("✅ Image captured successfully")
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        if self.captured_image is not None:
            # Save captured image for debugging
            cv2.imwrite("captured_face_debug.jpg", self.captured_image)
            print("💾 Debug image saved as 'captured_face_debug.jpg'")
            return True
        
        return False
    
    def convert_to_base64(self):
        """Convert captured image to base64 format for API."""
        if self.captured_image is None:
            return False
            
        print("\n🔄 CONVERTING IMAGE TO BASE64")
        print("=" * 50)
        
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_image)
            
            # Convert to base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=90)
            img_bytes = buffer.getvalue()
            
            # Create base64 string
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            self.captured_base64 = f"data:image/jpeg;base64,{img_base64}"
            
            print(f"✅ Image converted to base64")
            print(f"📊 Image size: {pil_image.size}")
            print(f"📊 Base64 length: {len(self.captured_base64)} characters")
            
            return True
            
        except Exception as e:
            print(f"❌ Error converting image: {e}")
            return False
    
    def test_server_connection(self):
        """Test if backend server is running."""
        print("\n🔌 TESTING SERVER CONNECTION")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.api_base}/../health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server is running")
                return True
        except:
            pass
            
        try:
            # Try a simple endpoint
            response = requests.options(f"{self.api_base}/auth/validate-face", timeout=5)
            print("✅ Backend server is running (validate-face endpoint accessible)")
            return True
        except Exception as e:
            print(f"❌ Cannot connect to backend server: {e}")
            print("💡 Make sure backend server is running on localhost:5000")
            return False
    
    def test_face_validation_detailed(self):
        """Test face validation with detailed debugging."""
        if not self.captured_base64:
            print("❌ No image to validate")
            return False
            
        print("\n🔍 DETAILED FACE VALIDATION TEST")
        print("=" * 50)
        
        # Prepare the request
        payload = {
            'face_image': self.captured_base64
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        print(f"📤 Sending request to: {self.api_base}/auth/validate-face")
        print(f"📊 Payload size: {len(json.dumps(payload))} bytes")
        
        try:
            # Send request with timeout
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/auth/validate-face",
                json=payload,
                headers=headers,
                timeout=30
            )
            end_time = time.time()
            
            # Log response details
            print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
            print(f"📈 Status Code: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            
            # Parse response
            try:
                response_data = response.json()
                print(f"📄 Response Body:")
                print(json.dumps(response_data, indent=2))
            except:
                print(f"📄 Raw Response: {response.text}")
                response_data = {}
            
            # Analyze results
            if response.status_code == 200:
                if response_data.get('valid', False):
                    print("✅ Face validation SUCCESSFUL")
                    return True
                else:
                    print("❌ Face validation FAILED")
                    print(f"🔍 Reason: {response_data.get('message', 'Unknown')}")
                    return False
            else:
                print(f"❌ API Error: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out (30 seconds)")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - backend server might be down")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def test_full_registration(self):
        """Test complete registration flow."""
        if not self.captured_base64:
            print("❌ No image for registration")
            return False
            
        print("\n👤 TESTING FULL REGISTRATION FLOW")
        print("=" * 50)
        
        # Create test user data
        import random
        user_id = random.randint(1000, 9999)
        test_user = {
            "name": f"Camera Test User {user_id}",
            "email": f"camera_test_{user_id}@example.com",
            "password": "TestPass123!",
            "face_image": self.captured_base64
        }
        
        print(f"👤 Test user: {test_user['name']}")
        print(f"📧 Email: {test_user['email']}")
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/signup",
                json=test_user,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"📈 Registration Status: {response.status_code}")
            
            if response.status_code == 201:
                response_data = response.json()
                print("✅ Registration SUCCESSFUL")
                print(f"🆔 User ID: {response_data.get('user_id')}")
                print(f"📧 Email: {response_data.get('email')}")
                print(f"💬 Message: {response_data.get('message')}")
                return True
            else:
                print("❌ Registration FAILED")
                try:
                    error_data = response.json()
                    print(f"🔍 Error: {error_data}")
                except:
                    print(f"🔍 Raw error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def run_complete_test(self):
        """Run the complete camera face test."""
        print("🎯 CAMERA FACE VALIDATION COMPLETE TEST")
        print("=" * 60)
        print("This test will:")
        print("1. Capture your face using camera")
        print("2. Test server connection")
        print("3. Validate face recognition")
        print("4. Test full registration flow")
        print("=" * 60)
        
        # Step 1: Capture face
        if not self.capture_face_from_camera():
            print("❌ Test failed: Could not capture face")
            return
        
        # Step 2: Convert to base64
        if not self.convert_to_base64():
            print("❌ Test failed: Could not convert image")
            return
        
        # Step 3: Test server connection
        if not self.test_server_connection():
            print("❌ Test failed: Server not accessible")
            return
        
        # Step 4: Test face validation
        validation_success = self.test_face_validation_detailed()
        
        # Step 5: Test registration if validation works
        if validation_success:
            registration_success = self.test_full_registration()
        else:
            print("\n⚠️  Skipping registration test due to validation failure")
            registration_success = False
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Camera Capture:     {'✅ PASS' if self.captured_image is not None else '❌ FAIL'}")
        print(f"Image Conversion:   {'✅ PASS' if self.captured_base64 is not None else '❌ FAIL'}")
        print(f"Server Connection:  ✅ PASS")
        print(f"Face Validation:    {'✅ PASS' if validation_success else '❌ FAIL'}")
        print(f"Full Registration:  {'✅ PASS' if registration_success else '❌ FAIL'}")
        
        if validation_success and registration_success:
            print("\n🎉 ALL TESTS PASSED! Face validation is working correctly.")
        elif validation_success:
            print("\n✅ Face validation works, but registration had issues.")
        else:
            print("\n🚨 Face validation failed. Check the detailed output above.")
            print("\n🔧 DEBUGGING TIPS:")
            print("- Ensure good lighting when capturing")
            print("- Look directly at the camera")
            print("- Make sure your face is clearly visible")
            print("- Check if backend server is running with development bypass")
        
        print(f"\n📁 Debug image saved as: captured_face_debug.jpg")

def main():
    """Main function to run the camera test."""
    test = CameraFaceTest()
    test.run_complete_test()

if __name__ == "__main__":
    main()