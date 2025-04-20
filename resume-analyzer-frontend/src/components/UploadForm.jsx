// UploadForm.jsx
import { useState } from "react";
import { uploadResume } from "../api/resumeApi";

const UploadForm = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [jobRole, setJobRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setError("Please select a file to upload.");
      return;
    }

    if (!jobRole.trim()) {
      setError("Please enter a job role.");
      return;
    }

    setLoading(true);
    setError(null);

    const result = await uploadResume(selectedFile, jobRole);

    setLoading(false);

    if (result.error) {
      setError(result.error);
    } else {
      onUploadSuccess(result);
    }
  };

  return (
    <div className="animate-border-glow p-6 bg-black border-2 border-yellow-400/80 rounded-lg shadow-lg shadow-yellow-400/30 relative overflow-hidden">
      <div className="relative z-10">
        <h2 className="title-text text-2xl font-bold mb-6 text-yellow-400 glow-text text-center">
          Upload Your Resume
        </h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="relative">
            <input 
              type="file" 
              onChange={handleFileChange} 
              className="content-text w-full p-3 bg-black border-2 border-yellow-400/50 rounded-lg text-yellow-400 focus:border-yellow-400 focus:outline-none hover:border-yellow-400 transition-colors duration-200" 
              accept=".pdf,.doc,.docx"
            />
          </div>
          <input
            type="text"
            value={jobRole}
            onChange={(e) => setJobRole(e.target.value)}
            placeholder="Enter target job role (e.g., Senior Software Engineer, Product Manager)"
            className="content-text p-3 bg-black border-2 border-yellow-400/50 rounded-lg text-yellow-400 placeholder-yellow-400/40 focus:border-yellow-400 focus:outline-none hover:border-yellow-400 transition-colors duration-200"
          />
          <button
            type="submit"
            className="content-text bg-transparent hover:bg-yellow-400 border-2 border-yellow-400 text-yellow-400 hover:text-black p-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-yellow-400/50 mt-2"
            disabled={loading}
          >
            {loading ? "Uploading..." : "Upload Resume"}
          </button>
          {error && (
            <p className="text-red-500 mt-2 content-text text-center">{error}</p>
          )}
        </form>
      </div>
      <div className="absolute inset-0 bg-gradient-to-r from-yellow-400/0 via-yellow-400/10 to-yellow-400/0 rounded-lg blur-lg"></div>
    </div>
  );
};

export default UploadForm;