import React, { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useSocket } from '../hooks/useSocket';
import { LogOut, User, Clock, Bell } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const { connected, joinNotifications } = useSocket();

  useEffect(() => {
    // Join notifications room when component mounts
    if (connected) {
      joinNotifications();
    }
  }, [connected, joinNotifications]);

  const handleLogout = async () => {
    await logout();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center animated-bg">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen animated-bg">
      {/* Header */}
      <header className="bg-white bg-opacity-10 backdrop-blur-lg border-b border-white border-opacity-20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold text-white">Face Auth Dashboard</h1>
          </div>

          {/* Connection Status */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-white text-sm">
                {connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-lg transition-colors duration-200"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-8 mb-8 text-center animate-fade-in">
          {/* Profile Photo */}
          <div className="inline-block mb-6">
            {user.photo_path ? (
              <img
                src={`http://localhost:5000/uploads/${user.photo_path}`}
                alt="Profile"
                className="w-24 h-24 rounded-full border-4 border-white border-opacity-30 shadow-lg"
              />
            ) : (
              <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center border-4 border-white border-opacity-30">
                <User className="w-12 h-12 text-white" />
              </div>
            )}
          </div>

          {/* Welcome Message */}
          <h2 className="text-3xl font-bold text-white mb-2 animate-slide-up">
            Welcome back, {user.name}!
          </h2>
          <p className="text-white text-opacity-80 animate-slide-up" style={{animationDelay: '0.1s'}}>
            You have successfully logged in using face recognition
          </p>

          {/* Success Badge */}
          <div className="inline-flex items-center mt-4 px-4 py-2 bg-green-500 bg-opacity-20 border border-green-400 border-opacity-30 rounded-full animate-scale-in" style={{animationDelay: '0.2s'}}>
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
            <span className="text-green-100 text-sm font-medium">Authentication Successful</span>
          </div>
        </div>

        {/* User Information */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Account Details */}
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-6 animate-scale-in">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <User className="w-5 h-5 mr-2" />
              Account Details
            </h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-white text-opacity-70 text-sm">Name</label>
                <p className="text-white font-medium">{user.name}</p>
              </div>
              
              <div>
                <label className="block text-white text-opacity-70 text-sm">Email</label>
                <p className="text-white font-medium">{user.email}</p>
              </div>
              
              <div>
                <label className="block text-white text-opacity-70 text-sm">Account Status</label>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-green-100 font-medium">Verified</span>
                </div>
              </div>
            </div>
          </div>

          {/* Login History */}
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-6 animate-scale-in" style={{animationDelay: '0.1s'}}>
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Login History
            </h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-white text-opacity-70 text-sm">Account Created</label>
                <p className="text-white font-medium">{formatDate(user.created_at)}</p>
              </div>
              
              <div>
                <label className="block text-white text-opacity-70 text-sm">Last Login</label>
                <p className="text-white font-medium">{formatDate(user.last_login_at)}</p>
              </div>
              
              <div>
                <label className="block text-white text-opacity-70 text-sm">Login Method</label>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                  <span className="text-blue-100 font-medium">Face Recognition</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Real-time Notifications Section */}
        <div className="mt-8 bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-6 animate-fade-in" style={{animationDelay: '0.3s'}}>
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Bell className="w-5 h-5 mr-2" />
            Real-time Notifications
          </h3>
          
          <div className="text-white text-opacity-70">
            <p className="mb-2">🔔 Real-time notifications are active</p>
            <p className="mb-2">📧 Login notification email sent</p>
            <p className="text-sm">Notifications will appear here automatically when events occur.</p>
          </div>
        </div>

        {/* Security Information */}
        <div className="mt-8 bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-6 animate-fade-in" style={{animationDelay: '0.4s'}}>
          <h3 className="text-xl font-semibold text-white mb-4">🔒 Security Features</h3>
          
          <div className="grid md:grid-cols-3 gap-4 text-white text-opacity-80">
            <div className="text-center">
              <div className="w-12 h-12 bg-green-500 bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-2">
                <div className="w-6 h-6 bg-green-400 rounded-full"></div>
              </div>
              <h4 className="font-medium mb-1">Face Authentication</h4>
              <p className="text-sm">Secure biometric login</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-500 bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-2">
                <div className="w-6 h-6 bg-blue-400 rounded-full"></div>
              </div>
              <h4 className="font-medium mb-1">Encrypted Data</h4>
              <p className="text-sm">All data securely encrypted</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500 bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-2">
                <div className="w-6 h-6 bg-purple-400 rounded-full"></div>
              </div>
              <h4 className="font-medium mb-1">Real-time Alerts</h4>
              <p className="text-sm">Instant login notifications</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;