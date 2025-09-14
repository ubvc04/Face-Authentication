"""
Health check route for monitoring.
"""
from flask import Blueprint, jsonify
from datetime import datetime
import os

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'service': 'face-auth-backend',
        'environment': os.getenv('FLASK_ENV', 'development')
    })


@health_bp.route('/api/health', methods=['GET'])
def api_health_check():
    """API health check endpoint."""
    return health_check()