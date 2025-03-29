from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
from parser import extract_text_from_pdf, analyze_resume
from weasyprint import HTML
import pdfplumber
import re
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Resume Analyzer Backend is Running!"

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
            candidate_name, contact_info, matched_content = match_content_to_template(optimized_text)

            # ✅ Ensure all required arguments are passed correctly
            generate_final_pdf(candidate_name, contact_info, matched_content, optimized_filename)

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
    """Extracts candidate name, contact details, and sections, while ensuring proper structuring."""

    # Split text into lines and filter out empty ones
    lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]

    candidate_name = "Candidate Name"  # Default fallback name
    contact_info = ""  # Contact details placeholder
    matched_content = {}

    # Define expected sections (excluding "Contact Information")
    section_titles = {
        "summary": "Summary",
        "experience": "Experience",
        "education": "Education",
        "skills": "Skills",
        "projects": "Projects",
        "certifications": "Certifications",
        "activities": "Activities"
    }

    current_section = None
    section_data = {}

    # Regular expressions for contact information
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    phone_pattern = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    linkedin_pattern = re.compile(r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9-_/]+", re.IGNORECASE)
    github_pattern = re.compile(r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9-_/]+", re.IGNORECASE)

    extracted_contact_details = {
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None
    }

    # Process each line
    for line in lines:
        # Extract Name (First non-empty line is assumed to be the name)
        if candidate_name == "Candidate Name" and len(line.split()) > 1:
            candidate_name = line.strip()
            continue  # Skip to next line after setting the name

        # Detect and extract contact details
        if email_pattern.search(line):
            extracted_contact_details["email"] = email_pattern.search(line).group()
        if phone_pattern.search(line):
            extracted_contact_details["phone"] = phone_pattern.search(line).group()
        if linkedin_pattern.search(line):
            extracted_contact_details["linkedin"] = linkedin_pattern.search(line).group()
        if github_pattern.search(line):
            extracted_contact_details["github"] = github_pattern.search(line).group()

        # Identify sections
        normalized_line = line.lower().strip().rstrip(":")  # Normalize section titles
        if normalized_line in section_titles:
            current_section = section_titles[normalized_line]
            section_data[current_section] = []  # Start new section
            continue

        # Assign content to the detected section
        if current_section:
            section_data[current_section].append(line)

    # Format contact details
    contact_info_parts = []
    if extracted_contact_details["phone"]:
        contact_info_parts.append(f"{extracted_contact_details['phone']}")
    if extracted_contact_details["email"]:
        contact_info_parts.append(f"<a href='mailto:{extracted_contact_details['email']}'>{extracted_contact_details['email']}</a>")
    if extracted_contact_details["linkedin"]:
        contact_info_parts.append(f"<a href='{extracted_contact_details['linkedin']}' target='_blank'>LinkedIn</a>")
    if extracted_contact_details["github"]:
        contact_info_parts.append(f"<a href='{extracted_contact_details['github']}' target='_blank'>GitHub</a>")

    contact_info = " | ".join(contact_info_parts) if contact_info_parts else "No contact info found."

    # Convert lists into formatted text
    for section, content_lines in section_data.items():
        matched_content[section] = "\n".join(content_lines)

    return candidate_name, contact_info, matched_content
def generate_final_pdf(candidate_name, contact_info, matched_content, output_filename):
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
                text-align: center;
                font-size: 10px;
                color: #333;
                margin-bottom: 10px;
            }}
            .contact a {{
                color: #002060;
                text-decoration: none;
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

        <!-- Candidate Name -->
        <div class="header">{candidate_name}</div>

        <!-- Contact Information -->
        <div class="contact">
            {contact_info}
        </div>
        <hr>
    """

    # Add sections dynamically, ensuring no duplicate headers
    for section_title, section_content in matched_content.items():
        if not section_content.strip():
            continue  # Skip empty sections

        html_content += f"<div class='section'><h2>{section_title}</h2><hr>"

        for line in section_content.split('\n'):
            # Make sure links are clickable
            if "http" in line or "www." in line:
                line = re.sub(r"(https?://[^\s]+)", r'<a href="\1" target="_blank">\1</a>', line)

            if line.startswith('-'):
                html_content += f"<ul><li>{line[1:].strip()}</li></ul>"
            else:
                html_content += f"<p>{line}</p>"
        html_content += "</div>"

    html_content += """
    </body>
    </html>
    """

    # Save PDF
    HTML(string=html_content).write_pdf(final_output_path)
    return final_output_path

if __name__ == '__main__':app.run(debug=True) 