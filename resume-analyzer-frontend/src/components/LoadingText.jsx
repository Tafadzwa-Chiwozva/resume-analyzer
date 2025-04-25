import { useEffect, useState } from 'react';

const LoadingText = ({ isVisible }) => {
  return (
    <div className={`loading-text ${isVisible ? 'visible' : ''}`}>
      Cooking
      <span className="loading-dots">
        <span>.</span>
        <span>.</span>
        <span>.</span>
      </span>
    </div>
  );
};

export default LoadingText; 