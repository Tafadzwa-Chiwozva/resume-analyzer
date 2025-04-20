import React from "react";

const ResumeFeedback = ({ data }) => {
  return (
    <div className="space-y-6">
      <h2 className="title-text text-2xl font-bold text-yellow-400 glow-text mb-6">
        Resume Analysis Results
      </h2>

      {/* Score in star */}
      <div className="star-score">
        <div className="star-score-content">
          {data.overall_score}
        </div>
      </div>

      {/* Strengths section */}
      <div>
        <h3 className="title-text text-xl font-bold text-yellow-400 glow-text mb-3">
          Strengths
        </h3>
        <ul className="list-disc list-inside space-y-2">
          {data.strengths.map((strength, index) => (
            <li key={index} className="content-text text-yellow-400/90 hover:text-yellow-400 transition-colors">
              {strength}
            </li>
          ))}
        </ul>
      </div>

      {/* Areas for Improvement section */}
      <div>
        <h3 className="title-text text-xl font-bold text-yellow-400 glow-text mb-3">
          Areas for Improvement
        </h3>
        <ul className="list-disc list-inside space-y-2">
          {data.improvements.map((improvement, index) => (
            <li key={index} className="content-text text-yellow-400/90 hover:text-yellow-400 transition-colors">
              {improvement}
            </li>
          ))}
        </ul>
      </div>

      {/* Actionable Changes section */}
      <div>
        <h3 className="title-text text-xl font-bold text-yellow-400 glow-text mb-3">
          Actionable Changes
        </h3>
        <ul className="list-disc list-inside space-y-2">
          {data.actionable_changes.map((change, index) => (
            <li key={index} className="content-text text-yellow-400/90 hover:text-yellow-400 transition-colors">
              {change}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ResumeFeedback;