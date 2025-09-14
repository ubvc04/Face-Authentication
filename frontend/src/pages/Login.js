import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Camera } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import CameraCapture from '../components/CameraCapture';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const Login = () => {
  const navigate = useNavigate();
  const { login, loginWithPassword, validateFace } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginMethod, setLoginMethod] = useState('face'); // 'face' or 'password'
  const [faceImage, setFaceImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFaceCapture = (imageData) => {
    setFaceImage(imageData);
  };

  const handleFaceValidation = async (imageData) => {
    try {
      await validateFace(imageData);
      return true;
    } catch (error) {
      toast.error(error.message);
      throw error;
    }
  };

  const handleFaceLogin = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) {
      toast.error('Email is required');
      return;
    }
    
    if (!faceImage) {
      toast.error('Please capture your face image');
      return;
    }

    setIsLoading(true);
    
    try {
      await login(email, faceImage);
      navigate('/dashboard');
    } catch (error) {
      // Error already handled by useAuth hook
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordLogin = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) {
      toast.error('Email is required');
      return;
    }
    
    if (!password.trim()) {
      toast.error('Password is required');
      return;
    }

    setIsLoading(true);
    
    try {
      await loginWithPassword(email, password);
      navigate('/dashboard');
    } catch (error) {
      // Error already handled by useAuth hook
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen animated-bg flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white bg-opacity-20 rounded-full mb-4">
            <Camera className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white">Welcome Back</h2>
          <p className="mt-2 text-white text-opacity-80">
            Login to your Face Auth account
          </p>
        </div>

        {/* Login Method Toggle */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-2">
          <div className="flex space-x-1">
            <button
              onClick={() => setLoginMethod('face')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
                loginMethod === 'face'
                  ? 'bg-white text-gray-900'
                  : 'text-white hover:bg-white hover:bg-opacity-10'
              }`}
            >
              <Camera className="w-4 h-4 inline mr-2" />
              Face Login
            </button>
            <button
              onClick={() => setLoginMethod('password')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
                loginMethod === 'password'
                  ? 'bg-white text-gray-900'
                  : 'text-white hover:bg-white hover:bg-opacity-10'
              }`}
            >
              <Lock className="w-4 h-4 inline mr-2" />
              Password
            </button>
          </div>
        </div>

        {/* Login Form */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-8">
          {loginMethod === 'face' ? (
            /* Face Login */
            <form onSubmit={handleFaceLogin} className="space-y-6">
              {/* Email Input */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-white mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    className="pl-10 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white bg-opacity-90 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              {/* Face Capture */}
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Face Authentication
                </label>
                <CameraCapture
                  onCapture={handleFaceCapture}
                  onValidation={handleFaceValidation}
                  isLoading={isLoading}
                />
              </div>

              {/* Login Button */}
              <button
                type="submit"
                disabled={!faceImage || isLoading}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-gray-900 bg-white hover:bg-gray-100 disabled:bg-gray-400 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <LoadingSpinner size="small" className="mr-2" />
                    Authenticating...
                  </div>
                ) : (
                  <>
                    <Camera className="w-5 h-5 mr-2" />
                    Login with Face
                  </>
                )}
              </button>
            </form>
          ) : (
            /* Password Login */
            <form onSubmit={handlePasswordLogin} className="space-y-6">
              {/* Email Input */}
              <div>
                <label htmlFor="email-pwd" className="block text-sm font-medium text-white mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="email-pwd"
                    name="email"
                    type="email"
                    required
                    className="pl-10 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white bg-opacity-90 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              {/* Password Input */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-white mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="password"
                    name="password"
                    type="password"
                    required
                    className="pl-10 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white bg-opacity-90 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>

              {/* Login Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-gray-900 bg-white hover:bg-gray-100 disabled:bg-gray-400 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <LoadingSpinner size="small" className="mr-2" />
                    Logging in...
                  </div>
                ) : (
                  <>
                    <Lock className="w-5 h-5 mr-2" />
                    Login with Password
                  </>
                )}
              </button>
            </form>
          )}

          {/* Signup Link */}
          <div className="mt-6 text-center">
            <p className="text-white text-opacity-70 text-sm">
              Don't have an account?{' '}
              <Link 
                to="/signup" 
                className="text-white font-medium hover:text-gray-200 transition-colors duration-200"
              >
                Sign up here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;