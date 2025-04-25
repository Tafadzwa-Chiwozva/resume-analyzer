import { useState } from "react";
import UploadForm from "./components/UploadForm";
import ResumeFeedback from "./components/ResumeFeedback";
import Gears from "./components/Gears";
import LoadingText from "./components/LoadingText";
import { downloadOptimizedResume } from "./api/resumeApi";

function App() {
  const [resumeData, setResumeData] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleUploadStart = () => {
    setIsProcessing(true);
  };

  const handleUploadSuccess = (result) => {
    setIsProcessing(false);
    if (result && result.ai_feedback) {
      setResumeData({
        ...result.ai_feedback,
        download_url: result.download_url
      });
    } else {
      setResumeData(null);
    }
  };

  const handleDownloadClick = () => {
    if (resumeData && resumeData.download_url) {
      downloadOptimizedResume(resumeData.download_url);
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-start py-12 px-4">
      <Gears isProcessing={isProcessing} />
      
      <div className="w-full max-w-2xl relative z-10">
        <div className="title-container mb-12">
          <div className="energy-streak animate-energy-streak" />
          <h1 className="text-center text-4xl font-bold text-yellow-400 glow-text relative z-10">
            AI Resume Optimizer
          </h1>
        </div>

        {/* Upload Form */}
        <div className="mb-8">
          <UploadForm 
            onUploadSuccess={handleUploadSuccess}
            onUploadStart={handleUploadStart}
          />
        </div>

        {/* Loading Text */}
        <LoadingText isVisible={isProcessing} />

        {/* If we have resumeData from the backend, show the feedback & download button */}
        {resumeData && resumeData.overall_score && (
          <div className="animate-border-glow p-6 bg-black border-2 border-yellow-400 rounded-lg shadow-lg shadow-yellow-400/20">
            <ResumeFeedback data={resumeData} />

            <button
              onClick={handleDownloadClick}
              className="mt-8 bg-transparent hover:bg-yellow-400 border-2 border-yellow-400 text-yellow-400 hover:text-black px-6 py-3 rounded-lg text-lg font-semibold transition-all duration-200 w-full"
            >
              Download Optimized Resume
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;