from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
from parser import extract_text_from_pdf, analyze_resume
from weasyprint import HTML
import pdfplumber

app = Flask(__name__)

# Define folder paths
UPLOAD_FOLDER = '../data/uploads'
PROCESSED_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "data/processed_resumes"))
REFERENCE_FOLDER = '../data/ref_resume'
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

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

        # Analyze and optimize resume
        job_category = request.form.get('job_category', 'General')
        feedback = analyze_resume(resume_text, job_category)

        if "optimized_resume" in feedback:
            optimized_text = feedback["optimized_resume"]

            # Generate optimized PDF matching the reference formatting
            optimized_filename = f"optimized_{filename}"
            optimized_file_path = os.path.join(app.config['PROCESSED_FOLDER'], optimized_filename) 
            
            # Apply reference formatting and generate final PDF
            matched_content = match_content_to_template(optimized_text)
            generate_final_pdf(matched_content, optimized_file_path)

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

def match_content_to_template(extracted_text):
    """Ensure proper section headers and structure without reference resume content."""
    sections = extracted_text.split('\n\n')

    # Expected section mappings (excluding "Contact Information")
    section_titles = [
        "Summary", "Experience", "Education", "Skills", "Projects", "Certifications", "Activities"
    ]

    matched_content = {}
    for i, section in enumerate(sections):
        # Skip redundant name and contact details
        if "4567 Main Street" in section or "janna@example.com" in section:
            continue

        section_title = section_titles[i] if i < len(section_titles) else f"Additional Info"
        matched_content[section_title] = section.strip()

    return matched_content

def generate_final_pdf(matched_content, output_filename):
    """Generate a PDF using WeasyPrint with formatted sections and blue headings, ensuring a one-page layout."""
    final_output_path = os.path.abspath(os.path.join(PROCESSED_FOLDER, output_filename))
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 10px;
            }}
            .header {{
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                color: #002060;
                margin-bottom: 5px;
            }}
            .contact {{
                display: flex;
                justify-content: space-between;
                font-size: 10px;
                color: #333;
                margin-bottom: 10px;
            }}
            h2 {{
                font-size: 14px;
                font-weight: bold;
                color: #002060;
                border-bottom: 2px solid #002060;
                padding-bottom: 5px;
                margin-top: 10px;
            }}
            p {{
                font-size: 10px;
                color: #333;
                margin: 2px 0;
            }}
            ul {{
                list-style-type: disc;
                margin-left: 15px;
            }}
            li {{
                font-size: 10px;
                color: #333;
            }}
            .section {{
                margin-bottom: 5px;
            }}
            .bold {{
                font-weight: bold;
            }}
            .blue {{
                color: #002060;
            }}
            hr {{
                border: 1px solid #002060;
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>

        <!-- Header with Name -->
        <div class="header">Janna Gardner</div>

        <!-- Contact Information -->
        <div class="contact">
            <div>4567 Main Street, Chicago, Illinois 98052</div>
            <div>(716) 555-0100 • janna@example.com</div>
        </div>
        <hr>

    """

    # Add sections dynamically, ensuring they fit within one page
    total_content_length = 0
    max_length = 5000  # Approximate character limit to fit one page

    for section_title, section_content in matched_content.items():
        if total_content_length > max_length:
            break  # Stop adding content if we exceed one page

        section_content = section_content[: max_length - total_content_length]  # Trim if necessary
        total_content_length += len(section_content)

        html_content += f"<div class='section'><h2>{section_title}</h2><hr>"  
        for line in section_content.split('\n'):
            if line.startswith('-'):
                html_content += f"<ul><li>{line[1:].strip()}</li></ul>"
            else:
                html_content += f"<p>{line}</p>"
        html_content += "</div>"

    html_content += """
    </body>
    </html>
    """

    # Save PDF with a one-page limit
    HTML(string=html_content).write_pdf(final_output_path, stylesheets=None, presentational_hints=True)
    return final_output_path

if __name__ == '__main__':
    app.run(debug=True)