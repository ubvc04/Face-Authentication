#!/usr/bin/env python3
"""
Simple test to capture a real webcam image and test face validation.
Run this script to test with actual camera input.
"""
import cv2
import base64
import requests
import json
from PIL import Image
import io

def capture_webcam_image():
    """Capture an image from webcam."""
    print("📷 Attempting to capture webcam image...")
    
    try:
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Cannot open webcam")
            return None
        
        print("✅ Webcam opened successfully")
        print("📸 Press SPACE to capture image, ESC to exit")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Failed to capture frame")
                break
            
            # Display the frame
            cv2.imshow('Webcam - Press SPACE to capture, ESC to exit', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 32:  # SPACE key
                print("📸 Image captured!")
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                pil_image = Image.fromarray(rgb_frame)
                
                # Release resources
                cap.release()
                cv2.destroyAllWindows()
                
                return pil_image
                
            elif key == 27:  # ESC key
                print("🚫 Capture cancelled")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return None
        
    except Exception as e:
        print(f"❌ Webcam capture failed: {e}")
        return None

def test_real_image(image):
    """Test face validation with real captured image."""
    if image is None:
        return False
    
    try:
        # Save captured image for inspection
        image.save("captured_face.jpg", "JPEG")
        print("💾 Saved captured image as 'captured_face.jpg'")
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        img_data = buffer.getvalue()
        img_b64 = base64.b64encode(img_data).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{img_b64}"
        
        print(f"📊 Image size: {image.size}")
        print(f"📊 Base64 length: {len(img_b64)} characters")
        
        # Test API endpoint
        print("🌐 Testing face validation API...")
        
        response = requests.post(
            'http://localhost:5000/api/auth/validate-face',
            json={'face_image': data_url},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('valid'):
                print("✅ Real image validation SUCCESSFUL!")
                return True
            else:
                print(f"❌ Real image validation FAILED: {result.get('message')}")
                return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Real image test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🎯 REAL WEBCAM FACE VALIDATION TEST")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding correctly")
            return
    except:
        print("❌ Backend server is not running on localhost:5000")
        print("   Please start the backend server first")
        return
    
    # Capture webcam image
    captured_image = capture_webcam_image()
    
    if captured_image:
        # Test with real image
        success = test_real_image(captured_image)
        
        if success:
            print("\n🎉 SUCCESS: Real webcam image validation worked!")
        else:
            print("\n🚨 FAILED: Real webcam image validation failed")
            print("   Check the saved 'captured_face.jpg' file")
            print("   Make sure your face is clearly visible and well-lit")
    else:
        print("\n❌ No image captured")

if __name__ == "__main__":
    main()