#!/usr/bin/env python3
"""
Complete Camera Face Capture Test
This simulates the exact frontend flow:
1. Capture face from camera
2. Convert to the same format as frontend (JPEG base64)
3. Call /api/auth/validate-face (same as frontend)
4. Call /api/auth/signup with the same data structure
5. Save to database and verify
"""

import cv2
import numpy as np
import base64
import requests
import json
import time
import sqlite3
from PIL import Image
import io

class FrontendFlowTest:
    def __init__(self):
        self.api_base = "http://localhost:5000/api"
        self.captured_image = None
        self.face_image_b64 = None
        self.user_data = None
        
    def capture_camera_image(self):
        """Capture image exactly like the frontend does."""
        print("🎥 FRONTEND CAMERA SIMULATION")
        print("=" * 50)
        print("Simulating react-webcam capture...")
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot access camera")
            return False
        
        # Set properties to match react-webcam
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        
        print("📷 Camera ready. Press SPACE to capture (like clicking 'Capture Face')")
        print("👀 Position your face in the center")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Mirror the image (like frontend webcam)
            frame = cv2.flip(frame, 1)
            
            # Resize to match frontend constraints
            frame_resized = cv2.resize(frame, (480, 360))
            
            # Add UI overlay
            cv2.putText(frame_resized, "SPACE: Capture Face | ESC: Cancel", 
                       (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame_resized, "Simulating Frontend Camera", 
                       (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            cv2.imshow('Frontend Camera Simulation', frame_resized)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                cap.release()
                cv2.destroyAllWindows()
                return False
            elif key == 32:  # SPACE
                self.captured_image = frame_resized.copy()
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if self.captured_image is not None:
            print("✅ Image captured successfully")
            cv2.imwrite("frontend_simulation_capture.jpg", self.captured_image)
            print("💾 Saved as 'frontend_simulation_capture.jpg'")
            return True
        
        return False
    
    def convert_to_frontend_format(self):
        """Convert image to exact format that frontend sends."""
        print("\n🔄 CONVERTING TO FRONTEND FORMAT")
        print("=" * 50)
        
        try:
            # Convert BGR to RGB (OpenCV uses BGR, frontend expects RGB)
            rgb_image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_image)
            
            # Convert to JPEG base64 (same as react-webcam getScreenshot())
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=95)  # High quality like frontend
            img_bytes = buffer.getvalue()
            
            # Create data URL format (same as frontend)
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            self.face_image_b64 = f"data:image/jpeg;base64,{img_base64}"
            
            print(f"✅ Converted to frontend format")
            print(f"📊 Image dimensions: {pil_image.size}")
            print(f"📊 JPEG size: {len(img_bytes)} bytes")
            print(f"📊 Base64 length: {len(self.face_image_b64)} characters")
            print(f"📊 Data URL prefix: {self.face_image_b64[:50]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Error converting image: {e}")
            return False
    
    def test_face_validation_api(self):
        """Test the exact API call that frontend makes."""
        print("\n🔍 TESTING FACE VALIDATION API")
        print("=" * 50)
        print("Calling /api/auth/validate-face (same as frontend)...")
        
        payload = {
            'face_image': self.face_image_b64
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/auth/validate-face",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            elapsed = time.time() - start_time
            
            print(f"⏱️  Response time: {elapsed:.2f}s")
            print(f"📈 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Validation successful!")
                print(f"📄 Response: {json.dumps(result, indent=2)}")
                return result.get('valid', False)
            else:
                print(f"❌ Validation failed!")
                try:
                    error = response.json()
                    print(f"📄 Error: {json.dumps(error, indent=2)}")
                except:
                    print(f"📄 Raw error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return False
    
    def test_signup_api(self):
        """Test the complete signup flow that frontend uses."""
        print("\n👤 TESTING SIGNUP API")
        print("=" * 50)
        
        # Create user data exactly like frontend
        self.user_data = {
            "name": "Camera Test User",
            "email": f"camera_test_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "face_image": self.face_image_b64
        }
        
        print(f"👤 User: {self.user_data['name']}")
        print(f"📧 Email: {self.user_data['email']}")
        print("🔐 Password: [HIDDEN]")
        print(f"📸 Face image: {len(self.user_data['face_image'])} chars")
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/signup",
                json=self.user_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"📈 Signup Status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print("✅ Signup successful!")
                print(f"📄 Response: {json.dumps(result, indent=2)}")
                return result
            else:
                print("❌ Signup failed!")
                try:
                    error = response.json()
                    print(f"📄 Error: {json.dumps(error, indent=2)}")
                except:
                    print(f"📄 Raw error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Signup failed: {e}")
            return None
    
    def verify_database_storage(self, signup_result):
        """Verify the user was actually saved to database."""
        print("\n💾 VERIFYING DATABASE STORAGE")
        print("=" * 50)
        
        if not signup_result:
            print("❌ No signup result to verify")
            return False
            
        try:
            # Connect to database
            db_path = "backend/instance/face_auth.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get user by email
            cursor.execute("""
                SELECT id, name, email, embedding, photo_path, is_verified, created_at 
                FROM users 
                WHERE email = ?
            """, (self.user_data['email'],))
            
            user_row = cursor.fetchone()
            
            if user_row:
                print("✅ User found in database!")
                print(f"🆔 ID: {user_row[0]}")
                print(f"👤 Name: {user_row[1]}")
                print(f"📧 Email: {user_row[2]}")
                print(f"🧬 Embedding: {'Present' if user_row[3] else 'Missing'}")
                print(f"📸 Photo: {user_row[4] if user_row[4] else 'None'}")
                print(f"✅ Verified: {user_row[5]}")
                print(f"📅 Created: {user_row[6]}")
                
                # Check if embedding exists and is valid
                if user_row[3]:
                    import pickle
                    try:
                        embedding = pickle.loads(user_row[3])
                        print(f"🧬 Embedding shape: {embedding.shape}")
                        print(f"🧬 Embedding preview: {embedding[:5]}")
                    except:
                        print("❌ Embedding data is corrupted")
                
                conn.close()
                return True
            else:
                print("❌ User not found in database!")
                conn.close()
                return False
                
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False
    
    def test_server_connection(self):
        """Quick server connectivity test."""
        print("🔌 Testing server connection...")
        try:
            response = requests.get(f"{self.api_base}/../health", timeout=5)
            return True
        except:
            try:
                response = requests.options(f"{self.api_base}/auth/validate-face", timeout=5)
                return True
            except:
                return False
    
    def run_complete_test(self):
        """Run the complete frontend simulation test."""
        print("🎯 FRONTEND FLOW SIMULATION TEST")
        print("=" * 60)
        print("This test simulates the exact frontend user flow:")
        print("1. Capture face using camera (like react-webcam)")
        print("2. Convert to JPEG base64 (like getScreenshot())")
        print("3. Call validate-face API (like useAuth.validateFace())")
        print("4. Call signup API (like useAuth.signup())")
        print("5. Verify database storage")
        print("=" * 60)
        
        # Test server connection
        if not self.test_server_connection():
            print("❌ Cannot connect to backend server!")
            print("💡 Make sure backend is running on localhost:5000")
            return
        
        print("✅ Server connection OK")
        
        # Step 1: Capture image
        if not self.capture_camera_image():
            print("❌ Test failed: Image capture cancelled")
            return
        
        # Step 2: Convert to frontend format
        if not self.convert_to_frontend_format():
            print("❌ Test failed: Image conversion failed")
            return
        
        # Step 3: Test face validation
        validation_success = self.test_face_validation_api()
        
        # Step 4: Test signup (regardless of validation result for debugging)
        signup_result = self.test_signup_api()
        
        # Step 5: Verify database
        db_success = self.verify_database_storage(signup_result)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPLETE TEST RESULTS")
        print("=" * 60)
        print(f"Camera Capture:     {'✅ PASS' if self.captured_image is not None else '❌ FAIL'}")
        print(f"Format Conversion:  {'✅ PASS' if self.face_image_b64 is not None else '❌ FAIL'}")
        print(f"Face Validation:    {'✅ PASS' if validation_success else '❌ FAIL'}")
        print(f"Signup API:         {'✅ PASS' if signup_result else '❌ FAIL'}")
        print(f"Database Storage:   {'✅ PASS' if db_success else '❌ FAIL'}")
        
        if validation_success and signup_result and db_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("The frontend flow should work correctly.")
        elif not validation_success:
            print("\n🚨 FACE VALIDATION FAILED!")
            print("This is the root cause of your 'face validation failed' error.")
            print("\n🔧 DEBUGGING RECOMMENDATIONS:")
            print("1. Check lighting conditions")
            print("2. Ensure face is clearly visible and centered")
            print("3. Try different angles")
            print("4. Check if development bypass is enabled")
        else:
            print("\n⚠️  PARTIAL SUCCESS")
            print("Face validation works but there are other issues.")

def main():
    """Main function."""
    test = FrontendFlowTest()
    test.run_complete_test()

if __name__ == "__main__":
    main()