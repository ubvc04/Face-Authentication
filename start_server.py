#!/usr/bin/env python3
"""
Simple Flask server with face recognition.
"""
import os
import sys

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Set environment variable for development bypass
os.environ['DEV_FACE_BYPASS'] = 'true'

try:
    from app import create_app, socketio
    
    print("🚀 Starting Face Auth Server...")
    app = create_app('development')
    
    print("✅ App created successfully")
    print("🔧 Development face bypass: ENABLED")
    print("🌐 Server will start on: http://localhost:5000")
    print("📋 API endpoints available at: http://localhost:5000/api")
    print("⚡ Press Ctrl+C to stop")
    print("-" * 50)
    
    # Run server
    socketio.run(
        app,
        host='127.0.0.1',
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True
    )
    
except KeyboardInterrupt:
    print("\n👋 Server stopped by user")
except Exception as e:
    print(f"❌ Server error: {e}")
    import traceback
    traceback.print_exc()