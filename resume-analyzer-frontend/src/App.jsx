import { useState } from "react";
import UploadForm from "./components/UploadForm";
import ResumeFeedback from "./components/ResumeFeedback";
import { downloadOptimizedResume } from "./api/resumeApi";

function App() {
  const [resumeData, setResumeData] = useState(null);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-5">
      <h1 className="text-center text-2xl font-bold mb-6">AI Resume Analyzer</h1>
      <UploadForm onUploadSuccess={setResumeData} />
      
      {resumeData && (
        <div className="mt-5">
          <ResumeFeedback data={resumeData} />
          <button
            className="mt-3 p-2 bg-green-500 hover:bg-green-700 rounded"
            onClick={() => downloadOptimizedResume(resumeData.filename)}
          >
            Download Optimized Resume
          </button>
        </div>
      )}
    </div>
  );
}

export default App;