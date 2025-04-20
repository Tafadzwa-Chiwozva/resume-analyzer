const Gears = ({ isProcessing }) => {
  return (
    <>
      <div className={`gear gear-left ${isProcessing ? 'animate-gear' : ''}`}>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          {/* Main gear body */}
          <path d="M50 10c-22.1 0-40 17.9-40 40s17.9 40 40 40 40-17.9 40-40-17.9-40-40-40zm0 12c15.5 0 28 12.5 28 28s-12.5 28-28 28-28-12.5-28-28 12.5-28 28-28z"/>
          
          {/* Inner rings */}
          <circle cx="50" cy="50" r="15" className="gear-inner-ring"/>
          <circle cx="50" cy="50" r="12" fill="none" strokeWidth="1.5" className="gear-stroke"/>
          <circle cx="50" cy="50" r="9" className="gear-inner-ring"/>
          
          {/* Bolt holes */}
          {[...Array(8)].map((_, i) => (
            <circle
              key={`bolt-${i}`}
              cx={50 + Math.cos(i * Math.PI / 4) * 20}
              cy={50 + Math.sin(i * Math.PI / 4) * 20}
              r="2"
              className="gear-hole"
            />
          ))}
          
          {/* Gear teeth - more mechanical looking */}
          {[...Array(20)].map((_, i) => (
            <path
              key={`tooth-${i}`}
              d={`M ${50 + Math.cos(i * Math.PI / 10) * 38} ${50 + Math.sin(i * Math.PI / 10) * 38} 
                 L ${50 + Math.cos(i * Math.PI / 10) * 45} ${50 + Math.sin(i * Math.PI / 10) * 45}
                 L ${50 + Math.cos((i + 0.5) * Math.PI / 10) * 45} ${50 + Math.sin((i + 0.5) * Math.PI / 10) * 45}
                 L ${50 + Math.cos((i + 0.5) * Math.PI / 10) * 38} ${50 + Math.sin((i + 0.5) * Math.PI / 10) * 38}`}
              className="gear-tooth"
            />
          ))}
          
          {/* Spokes */}
          {[...Array(6)].map((_, i) => (
            <path
              key={`spoke-${i}`}
              d={`M ${50 + Math.cos(i * Math.PI / 3) * 12} ${50 + Math.sin(i * Math.PI / 3) * 12}
                 L ${50 + Math.cos(i * Math.PI / 3) * 35} ${50 + Math.sin(i * Math.PI / 3) * 35}`}
              strokeWidth="3"
              className="gear-spoke"
            />
          ))}
        </svg>
      </div>
      <div className={`gear gear-right ${isProcessing ? 'animate-gear' : ''}`}>
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          {/* Main gear body */}
          <path d="M50 10c-22.1 0-40 17.9-40 40s17.9 40 40 40 40-17.9 40-40-17.9-40-40-40zm0 12c15.5 0 28 12.5 28 28s-12.5 28-28 28-28-12.5-28-28 12.5-28 28-28z"/>
          
          {/* Inner rings */}
          <circle cx="50" cy="50" r="15" className="gear-inner-ring"/>
          <circle cx="50" cy="50" r="12" fill="none" strokeWidth="1.5" className="gear-stroke"/>
          <circle cx="50" cy="50" r="9" className="gear-inner-ring"/>
          
          {/* Bolt holes */}
          {[...Array(8)].map((_, i) => (
            <circle
              key={`bolt-${i}`}
              cx={50 + Math.cos(i * Math.PI / 4) * 20}
              cy={50 + Math.sin(i * Math.PI / 4) * 20}
              r="2"
              className="gear-hole"
            />
          ))}
          
          {/* Gear teeth - more mechanical looking */}
          {[...Array(20)].map((_, i) => (
            <path
              key={`tooth-${i}`}
              d={`M ${50 + Math.cos(i * Math.PI / 10) * 38} ${50 + Math.sin(i * Math.PI / 10) * 38} 
                 L ${50 + Math.cos(i * Math.PI / 10) * 45} ${50 + Math.sin(i * Math.PI / 10) * 45}
                 L ${50 + Math.cos((i + 0.5) * Math.PI / 10) * 45} ${50 + Math.sin((i + 0.5) * Math.PI / 10) * 45}
                 L ${50 + Math.cos((i + 0.5) * Math.PI / 10) * 38} ${50 + Math.sin((i + 0.5) * Math.PI / 10) * 38}`}
              className="gear-tooth"
            />
          ))}
          
          {/* Spokes */}
          {[...Array(6)].map((_, i) => (
            <path
              key={`spoke-${i}`}
              d={`M ${50 + Math.cos(i * Math.PI / 3) * 12} ${50 + Math.sin(i * Math.PI / 3) * 12}
                 L ${50 + Math.cos(i * Math.PI / 3) * 35} ${50 + Math.sin(i * Math.PI / 3) * 35}`}
              strokeWidth="3"
              className="gear-spoke"
            />
          ))}
        </svg>
      </div>
    </>
  );
};

export default Gears; 