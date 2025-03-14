const API_BASE_URL = "http://127.0.0.1:5000"; // Your Flask backend URL

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

    return await response.json(); // Returns AI feedback and download URL
  } catch (error) {
    console.error("Error uploading resume:", error);
    return { error: error.message };
  }
};

export const downloadOptimizedResume = async (filename) => {
  window.open(`${API_BASE_URL}/download/${filename}`, "_blank");
};