from flask import Flask, request, jsonify
import os
from parser import extract_text_from_pdf, analyze_resume  # Import AI functions

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Resume Analyzer Backend is Running!"

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Extract text from resume
    try:
        extracted_text = extract_text_from_pdf(file_path)  # Correct function name
        job_category = request.form.get('job_category', 'General')
        ai_feedback = analyze_resume(extracted_text, job_category)  # Call AI function
        return jsonify({
            "filename": file.filename,
            "extracted_text": extracted_text,
            "ai_feedback": ai_feedback
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)