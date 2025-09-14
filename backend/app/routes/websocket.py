"""
WebSocket routes for real-time notifications and updates.
"""
from flask import Blueprint, request, session
from flask_socketio import emit, join_room, leave_room, disconnect
from app import socketio
import logging

logger = logging.getLogger(__name__)

websocket_bp = Blueprint('websocket', __name__)

@socketio.on('connect')
def on_connect():
    """Handle client connection."""
    user_id = session.get('user_id')
    if user_id:
        # Join user-specific room for targeted notifications
        join_room(f'user_{user_id}')
        logger.info(f"User {user_id} connected to WebSocket")
        
        # Send welcome message
        emit('connected', {
            'message': 'Connected to Face Auth real-time updates',
            'user_id': user_id
        })
    else:
        logger.warning("Unauthenticated WebSocket connection attempt")
        disconnect()

@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection."""
    user_id = session.get('user_id')
    if user_id:
        leave_room(f'user_{user_id}')
        logger.info(f"User {user_id} disconnected from WebSocket")

@socketio.on('join_notifications')
def on_join_notifications():
    """Join notifications room for real-time updates."""
    user_id = session.get('user_id')
    if user_id:
        join_room(f'user_{user_id}')
        emit('notification', {
            'type': 'success',
            'message': 'Connected to real-time notifications'
        })
        logger.info(f"User {user_id} joined notifications room")
    else:
        emit('error', {'message': 'Authentication required'})
        disconnect()

@socketio.on('ping')
def on_ping():
    """Handle ping for keeping connection alive."""
    emit('pong', {'timestamp': str(__import__('datetime').datetime.utcnow())})

# Helper functions for emitting notifications
def emit_user_notification(user_id, notification_type, message, data=None):
    """
    Emit notification to a specific user.
    
    Args:
        user_id: Target user ID
        notification_type: Type of notification (success, error, info, warning)
        message: Notification message
        data: Additional data to send
    """
    try:
        notification_data = {
            'type': notification_type,
            'message': message,
            'timestamp': str(__import__('datetime').datetime.utcnow())
        }
        
        if data:
            notification_data.update(data)
        
        socketio.emit('notification', notification_data, room=f'user_{user_id}')
        logger.info(f"Notification sent to user {user_id}: {message}")
        
    except Exception as e:
        logger.error(f"Failed to emit notification to user {user_id}: {e}")

def emit_login_success(user_id, user_name):
    """
    Emit login success notification.
    
    Args:
        user_id: User ID
        user_name: User's name
    """
    emit_user_notification(
        user_id,
        'success',
        f'Welcome back, {user_name}! You have successfully logged in.',
        {
            'event': 'login_success',
            'user_name': user_name
        }
    )

def emit_logout_notification(user_id):
    """
    Emit logout notification.
    
    Args:
        user_id: User ID
    """
    emit_user_notification(
        user_id,
        'info',
        'You have been logged out successfully.',
        {
            'event': 'logout'
        }
    )

def emit_security_alert(user_id, alert_message):
    """
    Emit security alert notification.
    
    Args:
        user_id: User ID
        alert_message: Security alert message
    """
    emit_user_notification(
        user_id,
        'warning',
        alert_message,
        {
            'event': 'security_alert'
        }
    )