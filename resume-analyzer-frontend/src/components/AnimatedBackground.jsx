import React from 'react';

const AnimatedBackground = ({ isAnimating }) => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {/* Sun */}
      <div className={`absolute top-8 right-8 w-20 h-20 rounded-full bg-yellow-400 
        ${isAnimating ? 'animate-sun-pulse' : ''} 
        shadow-[0_0_50px_#FFD700]`}
      />

      {/* Clouds */}
      <div className={`absolute left-0 top-4 w-full flex justify-between
        ${isAnimating ? 'animate-cloud-drift' : ''}`}>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="cloud">
            <div className="w-16 h-16 bg-gray-200/20 rounded-full" />
            <div className="w-24 h-24 bg-gray-200/20 rounded-full -mt-12 ml-8" />
            <div className="w-16 h-16 bg-gray-200/20 rounded-full -mt-20 ml-4" />
          </div>
        ))}
      </div>

      {/* Geese */}
      <div className={`absolute bottom-32 flex gap-8 
        ${isAnimating ? 'animate-geese-flight' : ''}`}>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="goose">
            <div className="w-8 h-4 bg-gray-400/40 skew-x-12 rounded-full" />
            <div className="w-3 h-3 bg-gray-400/40 rounded-full -mt-4 ml-6" />
            <div className={`w-6 h-1 bg-gray-400/40 absolute -mt-3 ml-1 origin-left 
              ${isAnimating ? 'animate-wing-flap' : ''}`} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnimatedBackground; 