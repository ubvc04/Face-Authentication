import { useState, useEffect, useContext, createContext } from 'react';
import toast from 'react-hot-toast';
import api from '../utils/api';

// Create auth context
const AuthContext = createContext();

// Auth provider component
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is authenticated on app load
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data.user);
    } catch (error) {
      // User not authenticated
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const signup = async (userData) => {
    try {
      const response = await api.post('/auth/signup', userData);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.error || 'Signup failed';
      toast.error(message);
      throw new Error(message);
    }
  };

  const verifyOTP = async (email, otp) => {
    try {
      const response = await api.post('/auth/verify-otp', { email, otp });
      toast.success('Account verified successfully!');
      return response.data;
    } catch (error) {
      const message = error.response?.data?.error || 'OTP verification failed';
      toast.error(message);
      throw new Error(message);
    }
  };

  const login = async (email, faceImage) => {
    try {
      const response = await api.post('/auth/login', { 
        email, 
        face_image: faceImage 
      });
      setUser(response.data.user);
      toast.success(`Welcome back, ${response.data.user.name}!`);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.error || 'Login failed';
      toast.error(message);
      throw new Error(message);
    }
  };

  const loginWithPassword = async (email, password) => {
    try {
      const response = await api.post('/auth/login-password', { 
        email, 
        password 
      });
      setUser(response.data.user);
      toast.success(`Welcome back, ${response.data.user.name}!`);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.error || 'Login failed';
      toast.error(message);
      throw new Error(message);
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
      setUser(null);
      toast.success('Logged out successfully');
    } catch (error) {
      // Even if logout fails on server, clear local state
      setUser(null);
      toast.success('Logged out');
    }
  };

  const resendOTP = async (email) => {
    try {
      const response = await api.post('/auth/resend-otp', { email });
      toast.success('OTP sent successfully!');
      return response.data;
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to send OTP';
      toast.error(message);
      throw new Error(message);
    }
  };

  const validateFace = async (faceImage) => {
    try {
      const response = await api.post('/auth/validate-face', { 
        face_image: faceImage 
      });
      return response.data;
    } catch (error) {
      const message = error.response?.data?.message || 'Face validation failed';
      throw new Error(message);
    }
  };

  const value = {
    user,
    loading,
    signup,
    verifyOTP,
    login,
    loginWithPassword,
    logout,
    resendOTP,
    validateFace,
    checkAuth
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}