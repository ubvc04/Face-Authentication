#!/usr/bin/env python3
"""
Startup script for Face Auth application.
Usage: python run_app.py [--config config_name]
"""

import os
import sys
import argparse
from app import create_app, db, socketio


def create_tables(app):
    """Create database tables if they don't exist."""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")


def main():
    """Main function to run the application."""
    parser = argparse.ArgumentParser(description='Run Face Auth application')
    parser.add_argument(
        '--config', 
        default='development',
        choices=['development', 'testing', 'production'],
        help='Configuration to use (default: development)'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host to bind to (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Set configuration
    os.environ['FLASK_ENV'] = args.config
    
    try:
        # Create app
        app = create_app(args.config)
        
        # Create database tables
        create_tables(app)
        
        print(f"Starting Face Auth application...")
        print(f"Configuration: {args.config}")
        print(f"Debug mode: {args.debug or app.debug}")
        print(f"Server: http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop")
        
        # Run the application
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug or app.debug,
            allow_unsafe_werkzeug=True  # For development only
        )
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()