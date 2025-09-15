#!/usr/bin/env python3
"""
Minimal server test and camera capture.
"""
import os
import sys
import cv2
import base64
import requests
import json
from PIL import Image
import io

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def test_server_only():
    """Test if server is accessible."""
    print("🔌 Testing server connection...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print(f"✅ Server responds: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False

def start_minimal_server():
    """Start a minimal Flask server for testing."""
    print("🚀 Starting minimal server...")
    
    os.environ['DEV_FACE_BYPASS'] = 'true'
    
    try:
        from app import create_app
        app = create_app('development')
        
        @app.route('/test')
        def test():
            return {'status': 'working'}
        
        print("✅ Server starting on http://localhost:5000")
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

def capture_and_test():
    """Capture image and test validation."""
    print("\n📸 CAMERA CAPTURE TEST")
    print("=" * 40)
    
    # Test server first
    if not test_server_only():
        print("Starting server...")
        # We'll need to start server in background
        return
    
    # Capture image
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    print("📷 Camera ready - Press SPACE to capture")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, "Press SPACE to capture", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Capture Face', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            # Convert to base64
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            
            buffer = io.BytesIO()
            pil_img.save(buffer, format='JPEG', quality=90)
            img_b64 = base64.b64encode(buffer.getvalue()).decode()
            data_url = f"data:image/jpeg;base64,{img_b64}"
            
            # Test validation
            print("\n🔍 Testing face validation...")
            try:
                response = requests.post(
                    "http://localhost:5000/api/auth/validate-face",
                    json={"face_image": data_url},
                    timeout=10
                )
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    print("✅ Face validation successful!")
                else:
                    print("❌ Face validation failed!")
                    
            except Exception as e:
                print(f"❌ API call failed: {e}")
            
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("🎯 MINIMAL FACE CAPTURE TEST")
    print("This will test the basic camera capture and validation")
    print("=" * 50)
    
    choice = input("Choose option:\n1. Start server\n2. Test capture (server must be running)\n3. Test server connection\nEnter choice (1-3): ")
    
    if choice == "1":
        start_minimal_server()
    elif choice == "2":
        capture_and_test()
    elif choice == "3":
        test_server_only()
    else:
        print("Invalid choice")