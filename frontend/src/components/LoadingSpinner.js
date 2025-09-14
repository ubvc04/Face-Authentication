import React from 'react';

const LoadingSpinner = ({ size = 'medium', className = '' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-16 h-16'
  };

  return (
    <div className={`inline-block ${sizeClasses[size]} ${className}`}>
      <div className="spinner border-2 border-gray-300 border-t-2 border-t-blue-600 rounded-full w-full h-full animate-spin"></div>
    </div>
  );
};

export default LoadingSpinner;