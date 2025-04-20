// resumeApi.js
const API_BASE_URL = "https://resume-analyzer-jj0k.onrender.com"; // Production URL on Render

export const uploadResume = async (file, jobCategory) => {
  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_category", jobCategory);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to upload resume");
    }

    // This JSON should contain: { message, download_url, ... } if successful
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
    return { error: error.message };
  }
};

export const downloadOptimizedResume = async (downloadUrl) => {
  // Just open the returned downloadUrl in a new tab
  window.open(`${API_BASE_URL}${downloadUrl}`, "_blank");
};