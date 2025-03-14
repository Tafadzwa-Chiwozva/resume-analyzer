import React from "react";

const ProcessedResume = ({ data }) => {
  return (
    <div className="bg-white p-6 shadow-lg rounded-lg w-96 mt-6 text-center">
      <h2 className="text-xl font-bold text-green-600">Optimized Resume</h2>
      <p className="mt-2 font-semibold">{data.name}</p>
      <p className="mt-2">{data.optimizedResume}</p>
    </div>
  );
};

export default ProcessedResume;