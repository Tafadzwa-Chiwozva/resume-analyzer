import { useState } from "react";
import UploadForm from "./components/UploadForm";
import ResumeFeedback from "./components/ResumeFeedback";
import ProcessedResume from "./components/ProcessedResume";
import { downloadOptimizedResume } from "./api/resumeApi";

function App() {
  const [resumeData, setResumeData] = useState(null);

  // This function is passed to UploadForm and called when the upload is successful
  const handleUploadSuccess = (result) => {
    // 'result' should be the JSON from Flask, e.g.:
    // {
    //   "message": "...",
    //   "download_url": "/download/optimized_sample_resume.pdf",
    //   "ai_feedback": { ... },
    //   ...
    // }
    setResumeData(result);
  };

  const handleDownloadClick = () => {
    if (resumeData && resumeData.download_url) {
      // Calls our function from resumeApi.js
      downloadOptimizedResume(resumeData.download_url);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-5">
      <h1 className="text-center text-2xl font-bold mb-4">AI Resume Analyzer</h1>

      {/* Upload Form */}
      <UploadForm onUploadSuccess={handleUploadSuccess} />

      {/* If we have resumeData from the backend, show the feedback & download button */}
      {resumeData && (
        <div className="mt-4 p-4 bg-gray-800 rounded">
          {/* If you have AI feedback fields in resumeData, pass them to ResumeFeedback */}
          
          {resumeData.ai_feedback && (
            <ResumeFeedback data={resumeData.ai_feedback} />
          )}
        
          

          {/* Download button */}
          <button
            onClick={handleDownloadClick}
            className="mt-4 bg-blue-500 hover:bg-blue-700 px-4 py-2 rounded"
          >
            Download Optimized Resume
          </button>
        </div>
      )}
    </div>
  );
}

export default App;