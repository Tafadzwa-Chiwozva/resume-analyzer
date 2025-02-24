from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
from parser import extract_text_from_pdf, analyze_resume
from fpdf import FPDF

app = Flask(__name__)
UPLOAD_FOLDER = '../data'
PROCESSED_FOLDER = '../data/processed_resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
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
        
        # Analyze the resume
        job_category = request.form.get('job_category', 'General')
        feedback = analyze_resume(resume_text, job_category)
        
        if "optimized_resume" in feedback:
            optimized_text = feedback["optimized_resume"]
            
            # Generate optimized PDF
            optimized_filename = f"optimized_{filename}"
            optimized_file_path = os.path.join(app.config['PROCESSED_FOLDER'], optimized_filename)
            print(f"Generating PDF at: {optimized_file_path}")
            generate_pdf(optimized_text, optimized_file_path)
            
            return jsonify({"message": "File uploaded and processed", "download_url": f"/download/{optimized_filename}"}), 200
        else:
            return jsonify({"error": "Failed to optimize resume"}), 500
    else:
        return jsonify({"error": "Invalid file format. Only PDFs are allowed."}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

def generate_pdf(text, file_path):
    pdf = FPDF()
    pdf.add_page()
    
    # Set up fonts
    pdf.set_font("Arial", size=16, style='B')
    
    # Extract sections from the text
    sections = text.split('\n\n')
    
    # Header
    header = sections[0].split('\n')
    name = header[0] if len(header) > 0 else "Name"
    contact_info = header[1] if len(header) > 1 else "Contact Info"
    linkedin = header[2] if len(header) > 2 else "LinkedIn"
    github = header[3] if len(header) > 3 else "GitHub"
    
    # Centered Header
    pdf.cell(0, 10, name, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, contact_info, ln=True, align='C')
    pdf.cell(0, 10, linkedin, ln=True, align='C')
    pdf.cell(0, 10, github, ln=True, align='C')
    
    # Add a line break
    pdf.ln(10)
    
    # Process each section
    for section in sections[1:]:
        lines = section.split('\n')
        title = lines[0]
        
        # Bold section title
        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(0, 10, title, ln=True)
        
        # Regular text for content
        pdf.set_font("Arial", size=12)
        for line in lines[1:]:
            if line.startswith('-'):
                pdf.cell(10)  # Indent bullet points
                pdf.multi_cell(0, 10, line)
            else:
                pdf.multi_cell(0, 10, line)
        
        # Add a line break between sections
        pdf.ln(5)
    
    # Output the PDF to the specified file path
    pdf.output(file_path)
    print(f"PDF generated at: {file_path}")

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    app.run(debug=True)