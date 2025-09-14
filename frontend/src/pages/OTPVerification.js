import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Mail, RefreshCw, CheckCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const OTPVerification = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { verifyOTP, resendOTP } = useAuth();
  
  const [otp, setOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes
  
  const email = location.state?.email || '';
  const message = location.state?.message || '';

  // Redirect if no email provided
  useEffect(() => {
    if (!email) {
      navigate('/signup');
    }
  }, [email, navigate]);

  // Countdown timer
  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => {
        setTimeLeft(timeLeft - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!otp.trim()) {
      toast.error('Please enter the OTP');
      return;
    }
    
    if (otp.length !== 6) {
      toast.error('OTP must be 6 digits');
      return;
    }

    setIsLoading(true);
    
    try {
      await verifyOTP(email, otp);
      navigate('/login', {
        state: {
          message: 'Account verified successfully! You can now login with your face.',
          email: email
        }
      });
    } catch (error) {
      // Error already handled by useAuth hook
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setIsResending(true);
    
    try {
      await resendOTP(email);
      setTimeLeft(600); // Reset timer
      setOtp(''); // Clear current OTP
    } catch (error) {
      // Error already handled by useAuth hook
    } finally {
      setIsResending(false);
    }
  };

  const handleOtpChange = (e) => {
    const value = e.target.value.replace(/\D/g, ''); // Only digits
    if (value.length <= 6) {
      setOtp(value);
    }
  };

  return (
    <div className="min-h-screen animated-bg flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white bg-opacity-20 rounded-full mb-4">
            <Mail className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white">Verify Your Email</h2>
          <p className="mt-2 text-white text-opacity-80">
            We've sent a verification code to
          </p>
          <p className="text-white font-medium">{email}</p>
        </div>

        {/* Verification Form */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-8">
          {message && (
            <div className="mb-4 p-3 bg-green-100 bg-opacity-20 border border-green-300 border-opacity-30 rounded-md">
              <p className="text-white text-sm">{message}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* OTP Input */}
            <div>
              <label htmlFor="otp" className="block text-sm font-medium text-white mb-2">
                Enter 6-digit verification code
              </label>
              <input
                id="otp"
                name="otp"
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength="6"
                required
                className="block w-full px-4 py-3 text-center text-2xl font-mono border border-gray-300 rounded-md shadow-sm bg-white bg-opacity-90 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="000000"
                value={otp}
                onChange={handleOtpChange}
              />
              
              {/* Timer */}
              <div className="mt-2 text-center">
                {timeLeft > 0 ? (
                  <p className="text-white text-opacity-70 text-sm">
                    Code expires in {formatTime(timeLeft)}
                  </p>
                ) : (
                  <p className="text-red-300 text-sm">
                    Code has expired. Please request a new one.
                  </p>
                )}
              </div>
            </div>

            {/* Verify Button */}
            <button
              type="submit"
              disabled={otp.length !== 6 || isLoading || timeLeft === 0}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-gray-900 bg-white hover:bg-gray-100 disabled:bg-gray-400 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <LoadingSpinner size="small" className="mr-2" />
                  Verifying...
                </div>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5 mr-2" />
                  Verify Account
                </>
              )}
            </button>
          </form>

          {/* Resend OTP */}
          <div className="mt-6 text-center">
            <p className="text-white text-opacity-70 text-sm mb-2">
              Didn't receive the code?
            </p>
            <button
              onClick={handleResendOTP}
              disabled={isResending || timeLeft > 540} // Allow resend after 1 minute
              className="text-white font-medium hover:text-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isResending ? (
                <div className="flex items-center justify-center">
                  <LoadingSpinner size="small" className="mr-2" />
                  Sending...
                </div>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 inline mr-1" />
                  Resend Code
                </>
              )}
            </button>
            {timeLeft > 540 && (
              <p className="text-white text-opacity-50 text-xs mt-1">
                Available in {formatTime(600 - timeLeft)}
              </p>
            )}
          </div>

          {/* Back to signup */}
          <div className="mt-6 text-center">
            <Link 
              to="/signup" 
              className="text-white text-opacity-70 text-sm hover:text-white transition-colors duration-200"
            >
              ← Back to signup
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OTPVerification;