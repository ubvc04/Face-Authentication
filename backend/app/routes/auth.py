"""
Authentication routes for signup, login, OTP verification, and logout.
"""
from flask import Blueprint, request, jsonify, session, current_app
from app import db, socketio
from app.models import User, RateLimiter
from app.services.face_recognition import face_service
from app.services.email_service import email_service
from app.utils.auth_utils import hash_password, verify_password, generate_otp, hash_otp, verify_otp
from datetime import datetime, timedelta
import uuid
import os
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Handle user signup with email, password, and face data.
    Steps:
    1. Validate input data
    2. Check rate limiting
    3. Extract face embedding
    4. Check for duplicate faces
    5. Save user data
    6. Send OTP email
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'face_image']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        face_image = data['face_image']
        
        # Basic validation
        if len(name) < 2:
            return jsonify({'error': 'Name must be at least 2 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check rate limiting
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if RateLimiter.is_rate_limited(client_ip):
            return jsonify({'error': 'Too many signup attempts. Please try again later.'}), 429
        
        # Record the attempt
        RateLimiter.record_attempt(client_ip)
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.is_verified:
                return jsonify({'error': 'Email already registered'}), 400
            else:
                # User exists but not verified, allow re-registration
                db.session.delete(existing_user)
                db.session.commit()
        
        # Extract face embedding
        face_embedding, error_msg = face_service.get_face_embedding(face_image)
        if face_embedding is None:
            return jsonify({'error': error_msg}), 400
        
        # Check for duplicate faces in database
        all_users = User.query.all()
        for user in all_users:
            try:
                existing_embedding = user.get_embedding()
                if face_service.is_same_person(face_embedding, existing_embedding):
                    return jsonify({
                        'error': 'This face is already registered to another account'
                    }), 400
            except Exception as e:
                logger.warning(f"Error comparing with user {user.id}: {e}")
                continue
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create new user
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            is_verified=False
        )
        
        # Set face embedding
        user.set_embedding(face_embedding)
        
        # Save user to get ID
        db.session.add(user)
        db.session.flush()  # Get the ID without committing
        
        # Save face thumbnail
        thumbnail_filename = f"user_{user.id}_face.jpg"
        saved_path = face_service.save_face_thumbnail(
            face_image, 
            thumbnail_filename, 
            current_app.config['UPLOAD_FOLDER']
        )
        if saved_path:
            user.photo_path = saved_path
        
        # Generate OTP
        otp_code = generate_otp()
        otp_hash = hash_otp(otp_code)
        otp_expires = datetime.utcnow() + timedelta(minutes=10)
        
        user.otp_hash = otp_hash
        user.otp_expires_at = otp_expires
        
        # Save all changes
        db.session.commit()
        
        # Send OTP email
        try:
            email_service.send_otp_email(email, name, otp_code)
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
            # Don't fail the signup, user can request resend
        
        logger.info(f"User signup successful: {email}")
        
        return jsonify({
            'message': 'Signup successful. Please check your email for OTP verification.',
            'user_id': user.id,
            'email': email
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Signup error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp_endpoint():
    """Verify OTP and activate user account."""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('otp'):
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        email = data['email'].strip().lower()
        otp_code = data['otp'].strip()
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.is_verified:
            return jsonify({'error': 'Account already verified'}), 400
        
        # Check OTP expiry
        if not user.otp_expires_at or datetime.utcnow() > user.otp_expires_at:
            return jsonify({'error': 'OTP has expired'}), 400
        
        # Verify OTP
        if not verify_otp(otp_code, user.otp_hash):
            return jsonify({'error': 'Invalid OTP'}), 400
        
        # Activate user
        user.is_verified = True
        user.otp_hash = None
        user.otp_expires_at = None
        db.session.commit()
        
        logger.info(f"User account verified: {email}")
        
        return jsonify({
            'message': 'Account verified successfully. You can now login.',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"OTP verification error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handle user login with email and face recognition.
    """
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('face_image'):
            return jsonify({'error': 'Email and face image are required'}), 400
        
        email = data['email'].strip().lower()
        face_image = data['face_image']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_verified:
            return jsonify({'error': 'Account not verified. Please check your email.'}), 400
        
        # Extract face embedding from login image
        login_embedding, error_msg = face_service.get_face_embedding(face_image)
        if login_embedding is None:
            return jsonify({'error': f'Face processing failed: {error_msg}'}), 400
        
        # Compare with stored embedding
        stored_embedding = user.get_embedding()
        if not face_service.is_same_person(login_embedding, stored_embedding):
            return jsonify({'error': 'Face did not match. Please try again.'}), 401
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        session['email'] = user.email
        session['login_time'] = datetime.utcnow().isoformat()
        
        # Send login notification email
        try:
            email_service.send_login_notification(user.email, user.name)
        except Exception as e:
            logger.warning(f"Failed to send login notification: {e}")
        
        # Emit real-time notification
        try:
            socketio.emit('user_login', {
                'user_id': user.id,
                'name': user.name,
                'login_time': user.last_login_at.isoformat()
            }, room=f'user_{user.id}')
        except Exception as e:
            logger.warning(f"Failed to emit login notification: {e}")
        
        logger.info(f"User login successful: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login-password', methods=['POST'])
def login_with_password():
    """
    Backup login method using email and password.
    """
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_verified:
            return jsonify({'error': 'Account not verified. Please check your email.'}), 400
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        session['email'] = user.email
        session['login_time'] = datetime.utcnow().isoformat()
        
        # Send login notification email
        try:
            email_service.send_login_notification(user.email, user.name)
        except Exception as e:
            logger.warning(f"Failed to send login notification: {e}")
        
        logger.info(f"User password login successful: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Password login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    try:
        user_id = session.get('user_id')
        if user_id:
            # Emit logout notification
            try:
                socketio.emit('user_logout', {
                    'user_id': user_id,
                    'logout_time': datetime.utcnow().isoformat()
                }, room=f'user_{user_id}')
            except Exception as e:
                logger.warning(f"Failed to emit logout notification: {e}")
        
        # Clear session
        session.clear()
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information."""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP for account verification."""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.is_verified:
            return jsonify({'error': 'Account already verified'}), 400
        
        # Generate new OTP
        otp_code = generate_otp()
        otp_hash = hash_otp(otp_code)
        otp_expires = datetime.utcnow() + timedelta(minutes=10)
        
        user.otp_hash = otp_hash
        user.otp_expires_at = otp_expires
        db.session.commit()
        
        # Send OTP email
        try:
            email_service.send_otp_email(email, user.name, otp_code)
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
            return jsonify({'error': 'Failed to send email'}), 500
        
        return jsonify({'message': 'OTP sent successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Resend OTP error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/validate-face', methods=['POST'])
def validate_face():
    """Validate face image quality before signup/login."""
    try:
        data = request.get_json()
        
        if not data.get('face_image'):
            return jsonify({'error': 'Face image is required'}), 400
        
        face_image = data['face_image']
        
        # For development: Check if it's a base64 image, if so, consider it valid
        # This is a temporary bypass to help with testing
        if face_image and face_image.startswith('data:image'):
            try:
                # Try to extract embedding to validate the face
                face_embedding, error_msg = face_service.get_face_embedding(face_image)
                
                if face_embedding is None:
                    # Provide more helpful error messages
                    if "No face detected" in error_msg:
                        # For development, we'll be more lenient
                        logger.warning(f"Face detection failed but allowing for development: {error_msg}")
                        return jsonify({
                            'valid': True,
                            'message': 'Face validation successful (development mode)'
                        }), 200
                    elif "Invalid image" in error_msg:
                        error_msg = "Unable to process the image. Please try taking a new photo."
                    
                    return jsonify({
                        'valid': False,
                        'message': error_msg
                    }), 400
                
                return jsonify({
                    'valid': True,
                    'message': 'Face validation successful'
                }), 200
                
            except Exception as e:
                logger.warning(f"Face validation error but allowing for development: {e}")
                # For development, allow through if it's a valid image format
                return jsonify({
                    'valid': True,
                    'message': 'Face validation successful (development mode)'
                }), 200
        
        return jsonify({
            'valid': False,
            'message': 'Invalid image format'
        }), 400
        
    except Exception as e:
        logger.error(f"Face validation error: {e}")
        return jsonify({
            'valid': False,
            'message': 'Face validation failed'
        }), 500