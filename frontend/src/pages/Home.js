import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Camera, Zap, Lock } from 'lucide-react';

const Home = () => {
  return (
    <div className="min-h-screen animated-bg">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white bg-opacity-20 rounded-full mb-6">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 animate-fade-in">
            Face Auth
          </h1>
          <p className="text-xl text-white text-opacity-90 max-w-2xl mx-auto animate-slide-up">
            Secure authentication using advanced face recognition technology. 
            Login with just your face - no passwords required.
          </p>
        </header>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-6 text-center animate-scale-in">
            <Camera className="w-12 h-12 text-white mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Face Recognition</h3>
            <p className="text-white text-opacity-80">
              State-of-the-art FaceNet technology for accurate and secure face authentication
            </p>
          </div>
          
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-6 text-center animate-scale-in" style={{animationDelay: '0.1s'}}>
            <Zap className="w-12 h-12 text-white mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Lightning Fast</h3>
            <p className="text-white text-opacity-80">
              Login in seconds with real-time face detection and matching
            </p>
          </div>
          
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-6 text-center animate-scale-in" style={{animationDelay: '0.2s'}}>
            <Lock className="w-12 h-12 text-white mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Highly Secure</h3>
            <p className="text-white text-opacity-80">
              Advanced encryption and one-face-per-account policy ensures maximum security
            </p>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-lg p-8 max-w-md mx-auto">
            <h2 className="text-2xl font-bold text-white mb-6">Get Started</h2>
            <div className="space-y-4">
              <Link
                to="/signup"
                className="block w-full py-3 px-6 bg-white text-gray-900 font-semibold rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                Create Account
              </Link>
              <Link
                to="/login"
                className="block w-full py-3 px-6 bg-transparent border-2 border-white text-white font-semibold rounded-lg hover:bg-white hover:text-gray-900 transition-colors duration-200"
              >
                Login
              </Link>
            </div>
            <p className="text-sm text-white text-opacity-70 mt-4">
              Secure • Fast • No Passwords
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;