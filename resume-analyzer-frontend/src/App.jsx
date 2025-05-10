import { useState, useRef } from 'react';
import ReactGA from 'react-ga4';
import UploadForm from "./components/UploadForm";
import ResumeFeedback from "./components/ResumeFeedback";
import Gears from "./components/Gears";
import LoadingText from "./components/LoadingText";
import { downloadOptimizedResume } from "./api/resumeApi";
import './App.css';

// Initialize Google Analytics
ReactGA.initialize('G-YBJ00WFG3T');

function App() {
  const [resumeData, setResumeData] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const fileInputRef = useRef(null);

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

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setDownloadUrl(window.URL.createObjectURL(selectedFile));
      setError(null);
      // Track file selection event
      ReactGA.event({
        category: 'Resume',
        action: 'File Selected',
        label: selectedFile.name
      });
    } else {
      setError('Please select a PDF file');
      setDownloadUrl(null);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!downloadUrl) {
      setError('Please select a file first');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Track resume upload event
      ReactGA.event({
        category: 'Resume',
        action: 'Upload Started',
        label: downloadUrl.split('/').pop()
      });

      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        body: new FormData(),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze resume');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);

      // Track successful analysis
      ReactGA.event({
        category: 'Resume',
        action: 'Analysis Complete',
        label: downloadUrl.split('/').pop()
      });
    } catch (err) {
      setError(err.message);
      // Track error event
      ReactGA.event({
        category: 'Error',
        action: 'Analysis Failed',
        label: err.message
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      // Track download event
      ReactGA.event({
        category: 'Resume',
        action: 'Download',
        label: downloadUrl.split('/').pop()
      });
      
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = 'optimized_resume.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setDownloadUrl(window.URL.createObjectURL(droppedFile));
      setError(null);
      // Track file drop event
      ReactGA.event({
        category: 'Resume',
        action: 'File Dropped',
        label: droppedFile.name
      });
    } else {
      setError('Please drop a PDF file');
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  // Track page view when component mounts
  ReactGA.send({ hitType: "pageview", page: window.location.pathname });

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-start py-12 px-4">
      {/* ResuMate Logo */}
      <div className="absolute top-6 left-8 z-20">
        <h2 className="text-2xl font-bold text-yellow-400 glow-text tracking-wider">
          ResuMate
        </h2>
      </div>

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
          <form onSubmit={handleSubmit} className="space-y-6">
            <div 
              className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={handleClick}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf"
                className="hidden"
              />
              <div className="space-y-2">
                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <div className="text-sm text-gray-400">
                  <span className="font-medium text-blue-400 hover:text-blue-300">
                    Click to upload
                  </span> or drag and drop
                </div>
                <p className="text-xs text-gray-500">PDF files only</p>
              </div>
            </div>

            {downloadUrl && (
              <div className="text-center text-sm text-gray-400">
                Selected file: {downloadUrl.split('/').pop()}
              </div>
            )}

            {error && (
              <div className="text-red-500 text-center text-sm">
                {error}
              </div>
            )}

            {isProcessing && (
              <div className="text-center">
                <LoadingText />
              </div>
            )}

            <div className="flex justify-center space-x-4">
              <button
                type="submit"
                disabled={!downloadUrl || isProcessing}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  !downloadUrl || isProcessing
                    ? 'bg-gray-600 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isProcessing ? 'Processing...' : 'Analyze Resume'}
              </button>

              {downloadUrl && (
                <button
                  type="button"
                  onClick={handleDownload}
                  className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
                >
                  Download
                </button>
              )}
            </div>
          </form>
        </div>

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