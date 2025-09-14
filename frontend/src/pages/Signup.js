import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Camera } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import CameraCapture from '../components/CameraCapture';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const Signup = () => {
  const navigate = useNavigate();
  const { signup, validateFace } = useAuth();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    faceImage: null
  });
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState('form'); // 'form' or 'camera'

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.name.trim()) {
      toast.error('Name is required');
      return;
    }
    
    if (!formData.email.trim()) {
      toast.error('Email is required');
      return;
    }
    
    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
    
    // Move to camera step
    setStep('camera');
  };

  const handleFaceCapture = async (imageData) => {
    setFormData({
      ...formData,
      faceImage: imageData
    });
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

  const handleSubmit = async () => {
    if (!formData.faceImage) {
      toast.error('Please capture your face image');
      return;
    }

    setIsLoading(true);
    
    try {
      const result = await signup({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        face_image: formData.faceImage
      });
      
      toast.success('Account created successfully! Please check your email for verification.');
      
      // Navigate to OTP verification with email
      navigate('/verify-otp', { 
        state: { 
          email: formData.email,
          message: result.message 
        } 
      });
      
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
            <User className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white">Create Account</h2>
          <p className="mt-2 text-white text-opacity-80">
            Join Face Auth for secure, passwordless authentication
          </p>
        </div>

        {/* Form */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-8">
          {step === 'form' ? (
            <form onSubmit={handleFormSubmit} className="space-y-6">
              {/* Name Input */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-white mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    className="pl-10 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white bg-opacity-90 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your full name"
                    value={formData.name}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

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
                    value={formData.email}
                    onChange={handleInputChange}
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
                    placeholder="Create a password"
                    value={formData.password}
                    onChange={handleInputChange}
                  />
                </div>
                <p className="mt-1 text-xs text-white text-opacity-70">
                  Password is only used for backup access. You'll login with your face.
                </p>
              </div>

              {/* Continue Button */}
              <button
                type="submit"
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-gray-900 bg-white hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
              >
                <Camera className="w-5 h-5 mr-2" />
                Continue to Face Capture
              </button>
            </form>
          ) : (
            /* Camera Step */
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-semibold text-white mb-2">
                  Capture Your Face
                </h3>
                <p className="text-white text-opacity-80 text-sm">
                  This will be used for secure face recognition login
                </p>
              </div>

              <CameraCapture
                onCapture={handleFaceCapture}
                onValidation={handleFaceValidation}
                isLoading={isLoading}
              />

              <div className="flex space-x-4">
                <button
                  onClick={() => setStep('form')}
                  className="flex-1 py-2 px-4 border border-gray-300 rounded-md text-white hover:bg-white hover:bg-opacity-10 transition-colors duration-200"
                >
                  Back
                </button>
                
                <button
                  onClick={handleSubmit}
                  disabled={!formData.faceImage || isLoading}
                  className="flex-1 py-2 px-4 bg-white text-gray-900 font-medium rounded-md hover:bg-gray-100 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center">
                      <LoadingSpinner size="small" className="mr-2" />
                      Creating Account...
                    </div>
                  ) : (
                    'Create Account'
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-white text-opacity-70 text-sm">
              Already have an account?{' '}
              <Link 
                to="/login" 
                className="text-white font-medium hover:text-gray-200 transition-colors duration-200"
              >
                Login here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;