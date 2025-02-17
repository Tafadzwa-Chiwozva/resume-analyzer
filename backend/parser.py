import pdfplumber
import docx
import openai  # Import OpenAI for AI-based feedback
import os

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Determine file type and extract text
def extract_resume_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Use PDF or DOCX.")

# AI-Powered Resume Analysis
# AI-Powered Resume Analysis (Updated OpenAI API)
import openai

# AI-Powered Resume Analysis (Fixed for OpenAI API v1.0+)
import openai

# AI-Powered Resume Analysis (Updated for GPT-3.5)
def analyze_resume(text):
    openai.api_key = "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"  # Replace with your actual API key

    prompt = f"""
    You are an AI career advisor reviewing a resume. Provide feedback on:
    - Overall structure
    - Clarity and conciseness
    - Missing skills or sections
    - Suggestions to improve

    Resume text:
    {text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Changed back (nvm)
        messages=[
            {"role": "system", "content": "You are a resume reviewer providing expert feedback."},
            {"role": "user", "content": prompt}
        ]
    )

    return response["choices"][0]["message"]["content"]

if __name__ == "__main__":
    test_resume = "data/sample_resume.pdf"  # Use the sample resume
    resume_text = extract_resume_text(test_resume)
    print("Extracted Resume Text:\n", resume_text)

    # Analyze the resume with AI
    ai_feedback = analyze_resume(resume_text)
    print("\nAI Feedback:\n", ai_feedback)