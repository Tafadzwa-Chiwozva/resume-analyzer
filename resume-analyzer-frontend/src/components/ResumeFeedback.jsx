import React from "react";

const ResumeFeedback = ({ data }) => {
  // 'data' is the object that includes overall_score, strengths, improvements, etc.
  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h2 className="text-lg font-semibold text-blue-400">Resume Analysis Results</h2>
      
      {/* Overall score */}
      <p className="text-yellow-400">Score: {data.overall_score}/10</p>

      {/* Strengths */}
      <div className="mt-2">
        <h3 className="text-green-400 font-semibold">Strengths</h3>
        <ul className="list-disc list-inside">
          {data.strengths?.map((strength, index) => (
            <li key={index}>{strength}</li>
          ))}
        </ul>
      </div>

      {/* Improvements */}
      <div className="mt-2">
        <h3 className="text-red-400 font-semibold">Areas for Improvement</h3>
        <ul className="list-disc list-inside">
          {data.improvements?.map((improvement, index) => (
            <li key={index}>{improvement}</li>
          ))}
        </ul>
      </div>

      {/* Optional: Actionable Changes */}
      {data.actionable_changes && data.actionable_changes.length > 0 && (
        <div className="mt-2">
          <h3 className="text-purple-400 font-semibold">Actionable Changes</h3>
          <ul className="list-disc list-inside">
            {data.actionable_changes.map((change, index) => (
              <li key={index}>{change}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResumeFeedback;