import React, { useRef, useCallback, useState } from 'react';
import Webcam from 'react-webcam';
import { Camera, RotateCcw, Check } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const CameraCapture = ({ 
  onCapture, 
  onValidation, 
  isLoading = false,
  showOverlay = true,
  className = ""
}) => {
  const webcamRef = useRef(null);
  const [isCaptured, setIsCaptured] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);

  const videoConstraints = {
    width: 480,
    height: 360,
    facingMode: "user"
  };

  const capture = useCallback(async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    
    if (imageSrc) {
      setCapturedImage(imageSrc);
      setIsCaptured(true);
      
      // Validate face if validation function provided
      if (onValidation) {
        try {
          await onValidation(imageSrc);
        } catch (error) {
          // If validation fails, reset capture
          setIsCaptured(false);
          setCapturedImage(null);
          return;
        }
      }
      
      // Call the capture callback
      if (onCapture) {
        onCapture(imageSrc);
      }
    }
  }, [webcamRef, onCapture, onValidation]);

  const retake = useCallback(() => {
    setIsCaptured(false);
    setCapturedImage(null);
  }, []);

  const confirm = useCallback(() => {
    if (capturedImage && onCapture) {
      onCapture(capturedImage);
    }
  }, [capturedImage, onCapture]);

  return (
    <div className={`relative ${className}`}>
      <div className="camera-container bg-gray-900 rounded-lg overflow-hidden">
        {!isCaptured ? (
          <div className="relative">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              className="w-full h-auto"
            />
            
            {showOverlay && (
              <div className="camera-overlay">
                <div className="absolute inset-0 flex items-center justify-center">
                  <Camera className="w-8 h-8 text-white opacity-60" />
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="relative">
            <img 
              src={capturedImage} 
              alt="Captured face" 
              className="w-full h-auto"
            />
            <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center">
              <Check className="w-12 h-12 text-green-400" />
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="mt-4 flex justify-center space-x-4">
        {!isCaptured ? (
          <button
            onClick={capture}
            disabled={isLoading}
            className="flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors duration-200"
          >
            {isLoading ? (
              <LoadingSpinner size="small" className="mr-2" />
            ) : (
              <Camera className="w-5 h-5 mr-2" />
            )}
            {isLoading ? 'Processing...' : 'Capture Face'}
          </button>
        ) : (
          <div className="flex space-x-3">
            <button
              onClick={retake}
              className="flex items-center px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Retake
            </button>
            <button
              onClick={confirm}
              className="flex items-center px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              <Check className="w-4 h-4 mr-2" />
              Use This Photo
            </button>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="mt-4 text-center text-sm text-gray-600">
        {!isCaptured ? (
          <p>Position your face in the center and click capture</p>
        ) : (
          <p>Review your photo and confirm or retake</p>
        )}
      </div>
    </div>
  );
};

export default CameraCapture;