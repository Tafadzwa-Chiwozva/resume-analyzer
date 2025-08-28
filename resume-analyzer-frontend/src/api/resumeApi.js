// resumeApi.js
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? "https://resume-optimizer.onrender.com"  // Production backend URL
  : "http://localhost:10000";                // Local development URL

const TIMEOUT_DURATION = 120000; // 2 minutes timeout

export const uploadResume = async (file, jobCategory) => {
  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_category", jobCategory);

    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_DURATION);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
      signal: controller.signal,
      credentials: 'omit' // Explicitly disable credentials
    });

    clearTimeout(timeoutId); // Clear timeout if request completes

    // Try to parse JSON response even if response is not ok
    let data;
    try {
      data = await response.json();
    } catch (e) {
      console.error('Failed to parse JSON response:', e);
      data = { error: 'Invalid response from server' };
    }
    
    if (!response.ok) {
      throw new Error(data.error || `Server error: ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error("Upload error:", error);
    
    // Handle specific error types
    if (error.name === 'AbortError') {
      return { 
        error: "Request timed out. The server took too long to respond.",
        details: "This might be because the server is under heavy load or starting up. Please try again in a few moments."
      };
    }
    
    return { 
      error: error.message || "Failed to upload resume",
      details: "The server might be starting up or under heavy load. Please try again in a few moments."
    };
  }
};

export const downloadOptimizedResume = async (downloadUrl) => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_DURATION);

    const response = await fetch(`${API_BASE_URL}${downloadUrl}`, {
      signal: controller.signal,
      headers: {
        'Accept': 'application/pdf',
      },
      credentials: 'omit'
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Failed to download resume: ${response.status}`);
    }
    window.open(`${API_BASE_URL}${downloadUrl}`, "_blank");
  } catch (error) {
    console.error("Download error:", error);
    if (error.name === 'AbortError') {
      return { error: "Download request timed out. Please try again." };
    }
    return { error: error.message };
  }
};