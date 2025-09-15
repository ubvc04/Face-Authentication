#!/usr/bin/env python3
"""
INTERACTIVE FACE VALIDATION TEST
This script will help you test the exact frontend flow step by step.
"""

import cv2
import base64
import requests
import json
from PIL import Image
import io
import time

def capture_face():
    """Capture your face using camera."""
    print("🎥 CAMERA CAPTURE")
    print("=" * 40)
    print("📋 Instructions:")
    print("- Look directly at the camera")
    print("- Ensure good lighting") 
    print("- Press SPACE when ready to capture")
    print("- Press ESC to cancel")
    print("\nOpening camera...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot access camera!")
        return None
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    captured_frame = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Camera error")
            break
            
        # Mirror image (like frontend)
        frame = cv2.flip(frame, 1)
        
        # Add instruction overlay
        cv2.putText(frame, "SPACE: Capture | ESC: Cancel", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, "Look directly at camera", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Show preview
        cv2.imshow('Face Capture - Ready?', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            print("❌ Capture cancelled")
            break
        elif key == 32:  # SPACE
            captured_frame = frame.copy()
            print("✅ Image captured!")
            # Show captured image for confirmation
            cv2.putText(captured_frame, "CAPTURED! Press any key to continue", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Captured Image', captured_frame)
            cv2.waitKey(2000)  # Show for 2 seconds
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    return captured_frame

def convert_to_frontend_format(frame):
    """Convert captured frame to exact frontend format."""
    print("\n🔄 CONVERTING TO FRONTEND FORMAT")
    print("=" * 40)
    
    try:
        # Convert BGR to RGB (OpenCV -> Frontend)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Convert to JPEG base64 (same as react-webcam)
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG', quality=92)  # Good quality
        img_bytes = buffer.getvalue()
        
        # Create data URL (exact frontend format)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{img_base64}"
        
        print(f"✅ Converted successfully")
        print(f"📏 Image size: {pil_image.size}")
        print(f"📦 JPEG size: {len(img_bytes):,} bytes")
        print(f"📜 Base64 length: {len(data_url):,} characters")
        
        # Save for debugging
        cv2.imwrite("debug_captured.jpg", frame)
        print(f"💾 Debug image saved as: debug_captured.jpg")
        
        return data_url
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return None

def test_face_validation(face_image_data):
    """Test the face validation API exactly like frontend does."""
    print("\n🔍 TESTING FACE VALIDATION API")
    print("=" * 40)
    print("🌐 Calling: http://localhost:5000/api/auth/validate-face")
    
    # Prepare request (exact frontend format)
    payload = {
        'face_image': face_image_data
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        print("📤 Sending validation request...")
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:5000/api/auth/validate-face',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        print(f"⏱️  Response time: {elapsed:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        # Parse response
        try:
            response_data = response.json()
            print(f"📄 Response Data:")
            print(json.dumps(response_data, indent=2))
        except:
            print(f"📄 Raw Response: {response.text}")
            response_data = {}
        
        # Analyze result
        if response.status_code == 200:
            if response_data.get('valid', False):
                print("\n✅ FACE VALIDATION SUCCESSFUL!")
                print(f"💬 Message: {response_data.get('message', 'Success')}")
                return True
            else:
                print("\n❌ FACE VALIDATION FAILED!")
                print(f"💬 Reason: {response_data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"\n❌ API ERROR: HTTP {response.status_code}")
            print(f"💬 Error: {response_data.get('error', 'Unknown error')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR!")
        print("🔧 Make sure backend server is running on localhost:5000")
        print("💡 Run the server first before testing")
        return False
    except requests.exceptions.Timeout:
        print("\n❌ REQUEST TIMEOUT!")
        print("⏰ Face validation took too long (>30 seconds)")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

def test_signup_flow(face_image_data):
    """Test the complete signup flow."""
    print("\n👤 TESTING COMPLETE SIGNUP FLOW")
    print("=" * 40)
    
    # Create test user data
    test_user = {
        "name": f"Test User {int(time.time())}",
        "email": f"test_{int(time.time())}@example.com", 
        "password": "TestPassword123!",
        "face_image": face_image_data
    }
    
    print(f"👤 Name: {test_user['name']}")
    print(f"📧 Email: {test_user['email']}")
    print("🔐 Password: [HIDDEN]")
    
    try:
        print("📤 Sending signup request...")
        response = requests.post(
            'http://localhost:5000/api/auth/signup',
            json=test_user,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ SIGNUP SUCCESSFUL!")
            print(f"📄 Response:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print("❌ SIGNUP FAILED!")
            try:
                error = response.json()
                print(f"📄 Error:")
                print(json.dumps(error, indent=2))
            except:
                print(f"📄 Raw Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return False

def main():
    """Main interactive test function."""
    print("🎯 INTERACTIVE FACE VALIDATION TEST")
    print("=" * 60)
    print("This test simulates the exact frontend flow:")
    print("1. 📸 Capture your face using camera")
    print("2. 🔄 Convert to frontend format (JPEG base64)")
    print("3. 🔍 Test face validation API")
    print("4. 👤 Test complete signup flow")
    print("=" * 60)
    
    # Check server
    try:
        requests.get("http://localhost:5000", timeout=2)
        print("✅ Backend server is accessible")
    except:
        print("❌ Backend server not accessible!")
        print("🔧 Please start the backend server first:")
        print("   cd backend && python simple_server.py")
        return
    
    input("\n🚀 Press ENTER to start camera capture...")
    
    # Step 1: Capture face
    captured_frame = capture_face()
    if captured_frame is None:
        print("❌ Test cancelled - no image captured")
        return
    
    # Step 2: Convert to frontend format
    face_data = convert_to_frontend_format(captured_frame)
    if face_data is None:
        print("❌ Test failed - image conversion failed")
        return
    
    # Step 3: Test validation
    validation_success = test_face_validation(face_data)
    
    # Step 4: Test signup (optional)
    if validation_success:
        test_signup = input("\n🤔 Validation passed! Test signup flow too? (y/n): ").lower().strip()
        if test_signup == 'y':
            signup_success = test_signup_flow(face_data)
        else:
            signup_success = None
    else:
        print("\n⚠️  Skipping signup test due to validation failure")
        signup_success = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"📸 Camera Capture:    {'✅ SUCCESS' if captured_frame is not None else '❌ FAILED'}")
    print(f"🔄 Format Conversion: {'✅ SUCCESS' if face_data is not None else '❌ FAILED'}")
    print(f"🔍 Face Validation:   {'✅ SUCCESS' if validation_success else '❌ FAILED'}")
    if signup_success is not None:
        print(f"👤 Signup Flow:       {'✅ SUCCESS' if signup_success else '❌ FAILED'}")
    
    if validation_success:
        print("\n🎉 VALIDATION WORKING!")
        print("Your face validation should work in the frontend too.")
    else:
        print("\n🚨 VALIDATION FAILED!")
        print("This explains why you see 'face validation failed' in frontend.")
        print("\n🔧 DEBUGGING TIPS:")
        print("- Check lighting conditions")
        print("- Ensure face is clearly visible and centered")
        print("- Try different camera angles")
        print("- Make sure you're looking directly at camera")
        print("- Check if development bypass is enabled in backend")
    
    print(f"\n📁 Debug files saved:")
    print(f"   - debug_captured.jpg (your captured image)")

if __name__ == "__main__":
    main()