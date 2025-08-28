from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
import re
from dotenv import load_dotenv
from parser import extract_text_from_pdf, analyze_resume
from weasyprint import HTML
from flask_cors import CORS

# Load environment variables from key.env file in root directory
load_dotenv('../key.env')
print(f"🔍 Environment check - OPENAI_API_KEY loaded: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
print(f"🔍 Current working directory: {os.getcwd()}")
print(f"🔍 .env file path: {os.path.join(os.getcwd(), '../key.env')}")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Resume Analyzer Backend is Running!"

# Define folder paths
UPLOAD_FOLDER = 'data/uploads'
PROCESSED_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "data/processed_resumes"))
REFERENCE_FOLDER = 'data/ref_resume'  # If you want to store a reference resume

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(REFERENCE_FOLDER, exist_ok=True)

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
    try:
        print("🔍 Starting resume upload process...")
        
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("❌ No selected file")
            return jsonify({"error": "No selected file"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Invalid file format. Only PDFs are allowed."}), 400
            
        print(f"📁 Processing file: {file.filename}")
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        print(f"✅ File saved to: {file_path}")

        # Extract text from the uploaded PDF
        print("📖 Extracting text from PDF...")
        resume_text = extract_text_from_pdf(file_path)
        print(f"✅ Extracted {len(resume_text)} characters")

        # (Optional) check for a job_category in the POST form data
        job_category = request.form.get('job_category', 'General')
        print(f"🎯 Job category: {job_category}")

        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return jsonify({"error": "OpenAI API key not configured"}), 500
        print(f"🔑 API key found: {api_key[:10]}...")

        # 1) Send the resume text to OpenAI for optimization
        print("🤖 Calling OpenAI API...")
        feedback = analyze_resume(resume_text, job_category)

        # 2) If successful, get the optimized text
        if "optimized_resume" in feedback:
            print("✅ OpenAI API call successful")
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
                "download_url": download_link,
                "ai_feedback": feedback  # <--- include the entire feedback dict
            }), 200
        else:
            print(f"❌ OpenAI API failed: {feedback}")
            return jsonify({"error": "Failed to optimize resume"}), 500
            
    except Exception as e:
        print(f"❌ Error in upload_file: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

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
        "technical skills": "Technical Skills",
        "technical experience": "Technical Skills",   # If GPT sometimes calls it “Technical Experience”
        "experience": "Experience",
        "leadership": "Leadership Experience",
        "leadership roles": "Leadership Experience",
        "leadership experience": "Leadership Experience",
        "volunteer": "Volunteer Experience",
        "volunteer work": "Volunteer Experience",
        "volunteer experience": "Volunteer Experience",
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
    Generate a PDF using WeasyPrint with styling:
      - Name in the center, large
      - Phone & Email on the left, smaller
      - LinkedIn & GitHub on the right, smaller
      - The HR line that was crossing out contact info is removed.
      - 'Education' is always listed as the first section
      - Each line becomes a bullet point
      
    
    """
    final_output_path = os.path.join(PROCESSED_FOLDER, output_filename)

    # 1) Extract 'Education' so we can render it first
    education_content = None
    if "Education" in matched_content:
        education_content = matched_content.pop("Education")

    # 2) Build the HTML/CSS
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: Letter;
                /* Reduce margins slightly to help fit more content on one page */
                margin: 0.6in;
            }}
            body {{
                font-family: Arial, sans-serif;
                color: #333;
                /* Increased font size */
                font-size: 15px; 
                line-height: 1.2em;
            }}
            .name {{
                font-size: 28px;
                text-align: center;
                font-weight: bold;
                color: #002060;
                margin-bottom: 20px;
            }}
            .contact-container {{
                width: 100%;
                overflow: auto;
                margin-bottom: 5px; /* Some spacing before the HR */
            }}
            .section-title {{
                font-size: 15px;
                font-weight: bold;
                color: #002060;
                margin-top: 10px;
                margin-bottom: 3px;
            }}
            /* Use a UL for each section so each line is a bullet */
            ul {{
                margin-top: 0;
                margin-bottom: 0;
                padding-left: 20px;
            }}
            li {{
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

        <!-- Contact Info (no HR above it, so it won't overlap) -->
        <div class="contact-container">
            {contact_info}
        </div>
        <hr />
    """

    # 3) Place 'Education' first (if present)
    if education_content and education_content.strip():
        html_content += """
        <div class="section">
            <div class="section-title">Education</div>
            <hr />
            <ul>
        """
        # Split lines and remove empty ones
        lines = [line.strip() for line in education_content.split("\n") if line.strip()]
        for line in lines:
            html_content += f"<li>{line}</li>"
        html_content += "</ul></div>"

    # 4) Render remaining sections in the order they're found
    for section_title, content in matched_content.items():
        if not content.strip():
            continue  # Skip empty sections
        html_content += f"""
        <div class="section">
            <div class="section-title">{section_title}</div>
            <hr />
            <ul>
        """
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        for line in lines:
            html_content += f"<li>{line}</li>"
        html_content += "</ul></div>"

    # Close the HTML
    html_content += """
    </body>
    </html>
    """

    # 5) Write PDF with WeasyPrint
    HTML(string=html_content).write_pdf(final_output_path)
    return final_output_path

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)