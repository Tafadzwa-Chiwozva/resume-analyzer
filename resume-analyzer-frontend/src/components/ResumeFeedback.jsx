import React from "react";

const ResumeFeedback = ({ data }) => {
  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h2 className="text-lg font-semibold text-blue-400">Resume Analysis Results</h2>
      <p className="text-yellow-400">Score: {data.ai_feedback.overall_score}/10</p>

      <div className="mt-2">
        <h3 className="text-green-400 font-semibold">Strengths</h3>
        <ul className="list-disc list-inside">
          {data.ai_feedback.strengths.map((strength, index) => (
            <li key={index}>{strength}</li>
          ))}
        </ul>
      </div>

      <div className="mt-2">
        <h3 className="text-red-400 font-semibold">Areas for Improvement</h3>
        <ul className="list-disc list-inside">
          {data.ai_feedback.improvements.map((improvement, index) => (
            <li key={index}>{improvement}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ResumeFeedback;