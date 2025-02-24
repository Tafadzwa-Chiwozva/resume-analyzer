from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
from parser import extract_text_from_pdf, analyze_resume
from weasyprint import HTML
import pdfplumber

app = Flask(__name__)

UPLOAD_FOLDER = '../data/uploads'
PROCESSED_FOLDER = '../data/processed_resumes'
REFERENCE_FOLDER = '../data/ref_resume'  # Folder for storing the reference resume

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['REFERENCE_FOLDER'] = REFERENCE_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(REFERENCE_FOLDER, exist_ok=True)

@app.route('/upload_template', methods=['POST'])
def upload_template():
    """Upload the reference resume to be used as a formatting template."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    template_path = os.path.join(app.config['REFERENCE_FOLDER'], "reference_resume.pdf")
    file.save(template_path)

    return jsonify({"message": "Template uploaded successfully"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process a user resume, applying the reference resume's formatting."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text from the uploaded PDF
        resume_text = extract_text_from_pdf(file_path)

        # Extract text from the reference resume
        reference_path = os.path.join(app.config['REFERENCE_FOLDER'], "reference_resume.pdf")
        if not os.path.exists(reference_path):
            return jsonify({"error": "Reference resume not found"}), 500
        
        reference_text = extract_text_from_pdf(reference_path)

        # Analyze and optimize resume
        job_category = request.form.get('job_category', 'General')
        feedback = analyze_resume(resume_text, job_category)

        if "optimized_resume" in feedback:
            optimized_text = feedback["optimized_resume"]

            # Generate optimized PDF matching the reference formatting
            optimized_filename = f"optimized_{filename}"
            optimized_file_path = os.path.join(app.config['PROCESSED_FOLDER'], optimized_filename)
            
            # Match formatting
            formatted_content = match_content_to_template(optimized_text, reference_text)
            generate_final_pdf(formatted_content, optimized_file_path)

            return jsonify({
                "message": "File uploaded and processed",
                "download_url": f"/download/{optimized_filename}"
            }), 200
        else:
            return jsonify({"error": "Failed to optimize resume"}), 500
    else:
        return jsonify({"error": "Invalid file format. Only PDFs are allowed."}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Allow users to download processed resumes."""
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

def match_content_to_template(optimized_text, reference_text):
    """Ensure the optimized resume follows the reference resume's structure."""
    ref_lines = reference_text.split("\n")
    opt_lines = optimized_text.split("\n")

    matched_content = {}
    for i in range(min(len(ref_lines), len(opt_lines))):
        matched_content[ref_lines[i]] = opt_lines[i]

    return matched_content

def generate_final_pdf(matched_content, output_path):
    """Generate a PDF with a format matching the reference resume."""
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            h1 { font-size: 16px; font-weight: bold; text-align: center; }
            h2 { font-size: 14px; font-weight: bold; }
            p { font-size: 12px; }
            ul { list-style-type: disc; margin-left: 20px; }
        </style>
    </head>
    <body>
    """
    
    for section_title, section_content in matched_content.items():
        html_content += f"<h2>{section_title}</h2>"
        for line in section_content.split("\n"):
            if line.startswith("-"):
                html_content += f"<ul><li>{line[1:].strip()}</li></ul>"
            else:
                html_content += f"<p>{line}</p>"
    
    html_content += """
    </body>
    </html>
    """

    HTML(string=html_content).write_pdf(output_path)

if __name__ == '__main__':
    app.run(debug=True)