// UploadForm.jsx
import { useState } from "react";
import { uploadResume } from "../api/resumeApi";

const UploadForm = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [jobCategory, setJobCategory] = useState("Software Engineer");
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

    setLoading(true);
    setError(null);

    const result = await uploadResume(selectedFile, jobCategory);

    setLoading(false);

    if (result.error) {
      setError(result.error);
    } else {
      // result should include: { message, download_url, ... } from the backend
      onUploadSuccess(result);
    }
  };

  return (
    <div className="p-4 bg-gray-800 text-white rounded-lg">
      <h2 className="text-lg font-semibold">Upload Your Resume</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <input type="file" onChange={handleFileChange} className="p-2" />
        <select
          value={jobCategory}
          onChange={(e) => setJobCategory(e.target.value)}
          className="p-2 bg-gray-700 border border-gray-600 rounded"
        >
          <option>Software Engineer</option>
          <option>Data Scientist</option>
          <option>Product Manager</option>
        </select>
        <button
          type="submit"
          className="bg-blue-500 p-2 rounded hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? "Uploading..." : "Upload Resume"}
        </button>
        {error && <p className="text-red-400">{error}</p>}
      </form>
    </div>
  );
};

export default UploadForm;