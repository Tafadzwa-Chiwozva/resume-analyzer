from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
import re
from parser import extract_text_from_pdf, analyze_resume
from weasyprint import HTML

app = Flask(__name__)

# Define folder paths
UPLOAD_FOLDER = 'data/uploads'
PROCESSED_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "data/processed_resumes"))
REFERENCE_FOLDER = 'data/ref_resume'  # If you want to store a reference resume

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(REFERENCE_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Resume Analyzer Backend is Running!"

@app.route('/upload_template', methods=['POST'])
def upload_template():
    """
    Upload the reference resume to be used as a formatting template (optional).
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    template_path = os.path.join(REFERENCE_FOLDER, "reference_resume.pdf")
    file.save(template_path)

    return jsonify({"message": "Template uploaded successfully"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload and process a user resume, applying an AI-optimized rewrite and
    final PDF formatting (blue/white style).
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Extract text from the uploaded PDF
        resume_text = extract_text_from_pdf(file_path)

        # (Optional) check for a job_category in the POST form data
        job_category = request.form.get('job_category', 'General')

        # 1) Send the resume text to OpenAI for optimization
        feedback = analyze_resume(resume_text, job_category)

        # 2) If successful, get the optimized text
        if "optimized_resume" in feedback:
            optimized_text = feedback["optimized_resume"]

            # Generate a new PDF that visually matches your desired style
            optimized_filename = f"optimized_{filename}"
            optimized_file_path = os.path.join(PROCESSED_FOLDER, optimized_filename)

            # 3) Extract structured content (name, contact, sections) from optimized text
            candidate_name, contact_info, matched_content = match_content_to_template(optimized_text)

            # 4) Build final PDF with the color scheme, fonts, and layout you want
            generate_final_pdf(
                candidate_name=candidate_name,
                contact_info=contact_info,
                matched_content=matched_content,
                output_filename=optimized_filename
            )

            # Print the link to the console (for easy copy-paste)
            download_link = f"/download/{optimized_filename}"
            print(f"✅ Your download link is: {download_link}")

            # Return JSON with the same link
            return jsonify({
                "message": f"File uploaded and processed successfully. Download your optimized resume at: {download_link}",
                "download_url": download_link
            }), 200
        else:
            return jsonify({"error": "Failed to optimize resume"}), 500
    else:
        return jsonify({"error": "Invalid file format. Only PDFs are allowed."}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Allow users to download processed resumes.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)

def match_content_to_template(extracted_text):
    """
    Parse the optimized resume text to find:
      - candidate name (first line)
      - contact info (phone, email, LinkedIn, GitHub)
      - sections (Skills, Projects, Education, etc.)
    Return them so we can place them into the final PDF with consistent styling.
    """
    # Split text into lines
    lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]

    # Defaults
    candidate_name = "Candidate Name"
    contact_info = ""
    matched_content = {}

    # Our recognized section titles
    section_titles = {
        "summary": "Summary",
        "skills": "Skills",
        "experience": "Experience",
        "projects": "Projects",
        "education": "Education",
        "certifications": "Certifications",
        "activities": "Activities",
        "awards": "Awards"
    }

    current_section = None
    section_data = {}

    # Regex for contact info
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

    for line in lines:
        # 1) First non-empty line after the AI rewrite is typically the candidate name
        if candidate_name == "Candidate Name" and len(line.split()) > 1:
            candidate_name = line.strip()
            continue

        # 2) Contact info detection
        if email_pattern.search(line):
            extracted_contact_details["email"] = email_pattern.search(line).group()
        if phone_pattern.search(line):
            extracted_contact_details["phone"] = phone_pattern.search(line).group()
        if linkedin_pattern.search(line):
            extracted_contact_details["linkedin"] = linkedin_pattern.search(line).group()
        if github_pattern.search(line):
            extracted_contact_details["github"] = github_pattern.search(line).group()

        # 3) Section detection
        normalized_line = line.lower().strip().rstrip(":")
        if normalized_line in section_titles:
            current_section = section_titles[normalized_line]
            section_data[current_section] = []
            continue

        # 4) If we are in a recognized section, add content to it
        if current_section:
            section_data[current_section].append(line)

    # Build contact info line
    contact_info_parts = []
    if extracted_contact_details["phone"]:
        contact_info_parts.append(extracted_contact_details["phone"])
    if extracted_contact_details["email"]:
        email_str = extracted_contact_details["email"]
        contact_info_parts.append(f"<a href='mailto:{email_str}'>{email_str}</a>")
    if extracted_contact_details["linkedin"]:
        contact_info_parts.append(f"<a href='{extracted_contact_details['linkedin']}' target='_blank'>LinkedIn</a>")
    if extracted_contact_details["github"]:
        contact_info_parts.append(f"<a href='{extracted_contact_details['github']}' target='_blank'>GitHub</a>")

    contact_info = " | ".join(contact_info_parts) if contact_info_parts else ""

    # Convert section content arrays into strings
    for section_title, lines_in_section in section_data.items():
        matched_content[section_title] = "\n".join(lines_in_section)

    return candidate_name, contact_info, matched_content

def generate_final_pdf(candidate_name, contact_info, matched_content, output_filename):
    """
    Generate a PDF using WeasyPrint with styling that matches the
    blue-and-white resume style shown in your screenshot.
    """
    final_output_path = os.path.join(PROCESSED_FOLDER, output_filename)

    # Simple HTML/CSS structure with a blue color scheme (#002060)
    # Adjust font sizes, margins, etc. as desired
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: Letter;
                margin: 1in;
            }}
            body {{
                font-family: Arial, sans-serif;
                color: #333;
            }}
            .name {{
                font-size: 22px;
                font-weight: bold;
                color: #002060;
                margin-bottom: 5px;
                text-transform: uppercase;
            }}
            .contact {{
                font-size: 10px;
                margin-bottom: 10px;
            }}
            .contact a {{
                color: #002060;
                text-decoration: none;
            }}
            .section-title {{
                font-size: 14px;
                font-weight: bold;
                color: #002060;
                margin-top: 15px;
                margin-bottom: 2px;
            }}
            .section-content {{
                font-size: 10px;
                line-height: 1.2em;
                margin-bottom: 5px;
            }}
            hr {{
                border: 0;
                border-top: 1px solid #002060;
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
        <!-- Candidate Name -->
        <div class="name">{candidate_name}</div>
        <!-- Contact Info -->
        <div class="contact">{contact_info}</div>
        <hr />
    """

    # Add each matched section with a heading
    for section_title, content in matched_content.items():
        if not content.strip():
            continue  # skip empty sections

        html_content += f"""
        <div class="section">
            <div class="section-title">{section_title}</div>
            <hr />
            <div class="section-content">
        """

        # For each line in the content, you can decide how to handle bullet points, etc.
        lines = content.split("\n")
        for line in lines:
            # If a line starts with '-', treat it like a bullet
            if line.strip().startswith("-"):
                html_content += f"<p style='margin-left: 10px;'>• {line[1:].strip()}</p>"
            else:
                html_content += f"<p>{line}</p>"

        html_content += "</div></div>"

    # Close out HTML
    html_content += """
    </body>
    </html>
    """

    # Write PDF
    HTML(string=html_content).write_pdf(final_output_path)
    return final_output_path

if __name__ == '__main__':
    app.run(debug=True)