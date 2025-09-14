# Face Auth - Modern Face Recognition Authentication System

A production-quality Flask web application that implements secure authentication using advanced face recognition technology. Users can sign up with face data, receive OTP verification via email, and login using only their face - no passwords required at login.

## 🚀 Features

- **Face Recognition Authentication**: Login using FaceNet-style embeddings
- **Email OTP Verification**: SMTP-based account activation
- **Real-time Notifications**: WebSocket-powered live updates
- **Face Uniqueness**: One face per account security
- **Modern UI**: React + Tailwind CSS with smooth animations
- **Password Backup**: Optional password login for recovery
- **Rate Limiting**: Protection against brute force attacks
- **Security-First**: Hashed passwords, encrypted face embeddings

## 🛠 Tech Stack

### Backend
- **Flask** (Python 3.11+)
- **SQLAlchemy** (SQLite database)
- **Flask-SocketIO** (WebSocket support)
- **FaceNet** (face recognition via facenet-pytorch)
- **SMTP** (email notifications)
- **bcrypt** (password hashing)

### Frontend
- **React** (18.2+)
- **Tailwind CSS** (modern styling)
- **Socket.IO Client** (real-time features)
- **React Webcam** (camera capture)
- **React Hot Toast** (notifications)
- **Framer Motion** (animations)

## 📋 Prerequisites

- **Python 3.11 or higher**
- **Node.js 16 or higher**
- **npm or yarn**
- **Webcam** (for face capture)
- **SMTP Email Account** (Gmail recommended)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Auth-Using-Face
```

### 2. Backend Setup

#### Create Python Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Download FaceNet Model
The FaceNet model will be automatically downloaded on first use. This may take a few minutes.

```bash
# Test the face recognition service
python -c "from app.services.face_recognition import face_service; print('Face recognition service ready!')"
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Environment Configuration

#### Copy Environment Template
```bash
# From project root
cp .env.example .env
```

#### Configure SMTP Settings
Edit `.env` file with your email settings:

```env
# SMTP Configuration (Example with Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Face Auth App
```

**Gmail Setup Instructions:**
1. Enable 2-Factor Authentication
2. Generate an "App Password" 
3. Use the app password in `SMTP_PASSWORD`

#### Configure Other Settings
```env
# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
FACE_MATCH_THRESHOLD=0.6

# Database
DATABASE_URL=sqlite:///face_auth.db

# CORS
CORS_ORIGINS=http://localhost:3000
```

### 5. Database Initialization

The database will be automatically created when you first run the backend:

```bash
cd backend
python run.py
```

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
# Activate virtual environment first
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

python run.py
```

The backend will run on `http://localhost:5000`

### Start Frontend Development Server

```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000`

## 📖 Usage Guide

### 1. Account Registration

1. Open `http://localhost:3000` in your browser
2. Click "Create Account"
3. Fill in your details (name, email, password)
4. Position your face in the camera and click "Capture Face"
5. Submit the form
6. Check your email for the OTP verification code
7. Enter the OTP to activate your account

### 2. Login

1. Go to the login page
2. Enter your email address
3. Position your face in the camera and click "Capture Face"
4. The system will authenticate using face recognition
5. Upon successful login, you'll be redirected to the dashboard

### 3. Dashboard Features

- Welcome message with your profile photo
- Last login time
- Real-time notifications
- Logout functionality

## 🧪 Testing the Application

### Manual Testing Checklist

#### Signup Flow
- [ ] Create account with valid details and face capture
- [ ] Receive OTP email within 1 minute
- [ ] Verify account with correct OTP
- [ ] Login using face recognition

#### Face Uniqueness
- [ ] Try registering different email with same face (should fail)
- [ ] Try registering same email again (should offer recovery)

#### Login Flow
- [ ] Login with face recognition
- [ ] Receive login notification email
- [ ] See real-time welcome notification
- [ ] View dashboard with profile info

#### Error Handling
- [ ] Invalid OTP (should show error)
- [ ] Expired OTP (should show error)
- [ ] No face detected (should show error)
- [ ] Multiple faces detected (should show error)

### API Testing with curl

#### Test Signup
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpass123",
    "face_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
  }'
```

#### Test Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "face_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
  }'
```

#### Test Current User
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Content-Type: application/json" \
  --cookie-jar cookies.txt
```

## 🔧 Configuration Options

### Face Recognition Settings

```env
# Cosine distance threshold for face matching
# Lower = more strict, Higher = more lenient
FACE_MATCH_THRESHOLD=0.6  # Range: 0.3-0.8
```

### Rate Limiting

```env
# Maximum signup attempts per IP
RATE_LIMIT_SIGNUP_ATTEMPTS=5
RATE_LIMIT_WINDOW_MINUTES=15
```

### OTP Settings

```env
# OTP expiry time in minutes
OTP_EXPIRY_MINUTES=10
```

## 📁 Project Structure

```
Auth-Using-Face/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── models/
│   │   │   └── __init__.py          # User model and database schema
│   │   ├── routes/
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   └── websocket.py         # WebSocket handlers
│   │   ├── services/
│   │   │   ├── email_service.py     # SMTP email service
│   │   │   └── face_recognition.py  # FaceNet ML service
│   │   └── utils/
│   │       └── auth_utils.py        # Password hashing, OTP utils
│   ├── tests/                       # Unit and integration tests
│   ├── uploads/                     # Face thumbnails storage
│   ├── requirements.txt             # Python dependencies
│   └── run.py                       # Application entry point
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CameraCapture.js     # Webcam capture component
│   │   │   └── LoadingSpinner.js    # Loading indicator
│   │   ├── hooks/
│   │   │   ├── useAuth.js           # Authentication context
│   │   │   └── useSocket.js         # WebSocket context
│   │   ├── pages/
│   │   │   ├── Home.js              # Landing page
│   │   │   ├── Signup.js            # Registration page
│   │   │   ├── Login.js             # Login page
│   │   │   ├── Dashboard.js         # User dashboard
│   │   │   └── OTPVerification.js   # OTP input page
│   │   ├── utils/
│   │   │   └── api.js               # Axios configuration
│   │   ├── App.js                   # Main React component
│   │   ├── index.js                 # React entry point
│   │   └── index.css                # Global styles
│   ├── package.json                 # Node.js dependencies
│   ├── tailwind.config.js           # Tailwind CSS config
│   └── postcss.config.js            # PostCSS config
├── .env.example                     # Environment template
└── README.md                        # This file
```

## 🔐 Security Features

### Face Data Protection
- Face images converted to mathematical embeddings only
- Original images not stored (optional thumbnails for display)
- Embeddings stored as encrypted JSON arrays

### Password Security
- bcrypt hashing with salt
- Minimum password requirements enforced
- Optional backup login method

### OTP Security
- Time-limited (10 minutes default)
- Single-use tokens
- Hashed storage in database

### Rate Limiting
- IP-based signup attempt limiting
- Configurable thresholds
- Automatic cleanup of old attempts

### Session Management
- Secure Flask sessions
- HTTP-only cookies
- CSRF protection

## 🚨 Troubleshooting

### Common Issues

#### Face Recognition Not Working
```bash
# Check if PyTorch is properly installed
python -c "import torch; print(torch.__version__)"

# Test face detection
python -c "from app.services.face_recognition import face_service; print('Service loaded successfully')"
```

#### Email Not Sending
1. Verify SMTP credentials in `.env`
2. Check Gmail app password setup
3. Test SMTP connection:
```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print("SMTP connection successful")
```

#### WebSocket Connection Issues
- Check CORS settings in `.env`
- Verify frontend and backend are on expected ports
- Check browser console for WebSocket errors

#### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm face_auth.db
python run.py  # Will recreate tables
```

### Performance Optimization

#### Face Recognition Speed
- CPU-only inference is sufficient for demo
- For production, consider GPU acceleration
- Reduce image resolution if needed

#### Memory Usage
- Monitor face embedding storage growth
- Consider periodic cleanup of unverified accounts
- Implement face thumbnail compression

## 🧪 Running Tests

### Unit Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Integration Tests
```bash
# Test full signup flow
python -m pytest tests/test_integration.py::test_signup_flow -v

# Test face recognition
python -m pytest tests/test_face_recognition.py -v
```

## 🚀 Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use production SMTP service (not Gmail)
- [ ] Enable HTTPS/SSL
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Monitor face embedding storage
- [ ] Implement proper logging
- [ ] Set up error tracking

### Environment Variables for Production
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
CORS_ORIGINS=https://yourdomain.com
```

## 📄 License

This project is for educational and demonstration purposes. Please ensure compliance with privacy laws and regulations when handling biometric data in production environments.

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the console/log output
3. Test with provided curl examples
4. Verify environment configuration

## 📊 Demo Script

A demo script is provided to test the complete flow:

```bash
cd backend
python demo_script.py
```

This will:
1. Create a test user with face data
2. Simulate OTP verification
3. Test face recognition login
4. Demonstrate WebSocket notifications

---

**Ready to test? Start both servers and visit `http://localhost:3000` to begin!** 🚀