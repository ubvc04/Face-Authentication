#!/usr/bin/env python3
"""
Simple server startup script for debugging.
"""
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

try:
    from app import create_app, socketio
    
    print("Creating Flask app...")
    app = create_app('development')
    
    print("Starting server on localhost:5000...")
    print("Development mode enabled")
    print("Press Ctrl+C to stop")
    
    # Run with SocketIO
    socketio.run(
        app,
        host='0.0.0.0',  # Listen on all interfaces
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True
    )
    
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)